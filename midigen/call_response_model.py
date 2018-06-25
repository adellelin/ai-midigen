from os.path import join
from os import walk
from os import mkdir
import sys
import shutil
import logging
import json
import pickle
import atexit
from errno import EEXIST
from errno import ENOENT
import numpy as np
import tensorflow as tf
from tensorflow.python.saved_model.builder import SavedModelBuilder
from tensorflow.python.saved_model import loader as tf_loader
import pretty_midi as pm
from midigen.encode import encoder_from_dict

_LOGGER = logging.getLogger('CallResponseModel')
_LOSS_REGRESSION_MULTIPLIER = 2.0
_STAGNATION_COUNT = 100000
_LR_MULTIPLIER = 0.8


class CallResponseModel:
    def __init__(self, hparams):
        self.hparams = hparams
        self.encoder_dict = hparams['encoder_dict']
        self.hidden_code_size = hparams['hidden_code_size']
        self.float_type = hparams['float_type']
        if self.float_type == 'float64':
            self.tf_type = tf.float64
        elif self.float_type == 'float32':
            self.tf_type = tf.float32
        else:
            raise ValueError()
        self.max_response_length = hparams['max_response_length']

        self.seed = None
        self.validation_ratio = None
        self.learning_rate = None
        self.gradient_clip = None
        self.keep_prob = None
        self.batch_size = None

        self._training_params = [
            'seed',
            'validation_ratio',
            'learning_rate',
            'gradient_clip',
            'keep_prob',
            'batch_size'
        ]

        for key in self._training_params:
            try:
                setattr(self, key, hparams[key])
            except KeyError:
                pass

        self.encoder = encoder_from_dict(hparams['encoder_dict'])

        self.eval_session = None

    def build_dataset(self, data_dir):
        _LOGGER.debug(f'building dataset from {data_dir}')

        np.random.seed(self.seed)

        calls = []
        responses = []

        for dirName, subdirList, fileList in walk(data_dir):
            cur_cr = {}
            for fname in fileList:
                if fname.endswith('.mid') and not fname[0] == '.':
                    try:
                        num = int(fname.replace('.mid', '').replace(' ', '_').split('_')[-1])
                    except ValueError:
                        _LOGGER.warning(f'file name does not end with integer {fname}')
                        continue

                    full_path = join(dirName, fname)
                    try:
                        midi = pm.PrettyMIDI(full_path)
                        assert len(midi.instruments[0].notes) > 3
                        cur_cr[num] = self.encoder.encode(midi, instrument_index=0)
                    except (AssertionError, IOError, KeyError):
                        _LOGGER.warning(f'Could not add midi file {join(dirName, fname)}.')

            for k in cur_cr.keys():
                if k % 2 == 1:
                    try:
                        cur_call = cur_cr[k]
                        cur_response = cur_cr[k + 1]
                        responses.append(cur_response)
                        calls.append(cur_call)
                    except KeyError:
                        _LOGGER.warning(f'Could not add index {k} from {dirName} because '
                                        f'it does not have a valid call/response.')

        _LOGGER.debug(f'building dataset from {data_dir}')

        call_len = calls[0].shape[0]
        for call, response in zip(calls, responses):
            assert call.shape[0] == call_len
            assert response.shape[0] == call_len

        num_examples = len(calls)
        num_training_examples = int(num_examples*(1.0-self.validation_ratio))
        indices = np.arange(num_examples, dtype=np.int32)
        np.random.shuffle(indices)

        dataset = {
            'calls': np.swapaxes(np.stack(calls), 0, 1),
            'responses': np.swapaxes(np.stack(responses), 0, 1),
            'training_indices': indices[:num_training_examples],
            'validation_indices': indices[num_training_examples:]
        }

        return dataset

    def core_graph(self, inputs, target_response):
        batch_size = tf.shape(inputs)[1]

        with tf.variable_scope('encoder', reuse=tf.AUTO_REUSE):
            if target_response is None:
                enc_cell = tf.nn.rnn_cell.BasicLSTMCell(self.hidden_code_size, name='lstm_cell')
                enc_outputs, enc_state = tf.nn.dynamic_rnn(
                    enc_cell, inputs, dtype=self.float_type, time_major=True)
            else:
                enc_cell = tf.contrib.rnn.LSTMBlockFusedCell(self.hidden_code_size)
                enc_outputs, enc_state = enc_cell(inputs, dtype=self.tf_type)

        with tf.variable_scope('decoder', reuse=tf.AUTO_REUSE):
            de_embed_init = np.random.normal(
                loc=0, scale=np.sqrt(2.0/(self.hidden_code_size + self.encoder.encoding_channels + 1)),
                size=(self.hidden_code_size, self.encoder.encoding_channels + 1))
            de_embed_w = tf.Variable(de_embed_init, name='de_embed_w', trainable=True, dtype=self.tf_type)
            de_embed_b = tf.Variable(np.zeros(self.encoder.encoding_channels + 1), dtype=self.tf_type,
                                     name='de_embed_b', trainable=True)

            if target_response is None:
                dec_cell = tf.nn.rnn_cell.BasicLSTMCell(self.hidden_code_size, name='rnn/lstm_cell')

                # generate GO vector
                go_np = np.zeros(self.encoder.encoding_channels + 1)
                go_np[-1] = 1
                go_template = tf.constant(go_np[np.newaxis, :], dtype=self.tf_type)
                go = tf.tile(go_template, [batch_size, 1])
                h_first, state_first = dec_cell(go, enc_state)

                de_first = tf.add(tf.matmul(h_first, de_embed_w), de_embed_b, name='out0')
                de_outputs = [de_first]
                dec_outputs = [h_first]
                dec_state = [state_first]
                dec_c = [state_first.c]
                dec_h = [state_first.h]
                prob = [go]

                for i in range(self.max_response_length - 1):
                    # prev_prob = tf.nn.softmax(de_outputs[-1], axis=1)
                    rng = tf.cast(tf.range(batch_size), dtype=tf.int64)
                    pos = tf.argmax(de_outputs[-1], axis=1)
                    indices = tf.stack([rng, pos], axis=1)
                    shape = tf.cast(tf.stack([batch_size, self.encoder.encoding_channels + 1]), dtype=tf.int64)

                    values = tf.ones(tf.reshape(batch_size, [1]), dtype=self.tf_type)
                    prev_prob_sharp = tf.scatter_nd(
                        indices,
                        values,
                        shape
                    )

                    h_cur, state_cur = dec_cell(prev_prob_sharp, dec_state[-1])
                    dec_outputs.append(h_cur)
                    de_cur = tf.add(tf.matmul(h_cur, de_embed_w), de_embed_b, name='out' + str(i + 1))
                    de_outputs.append(de_cur)
                    dec_state.append(state_cur)
                    dec_c.append(state_cur.c)
                    dec_h.append(state_cur.h)
                    prob.append(prev_prob_sharp)

                dec_outputs = tf.stack(dec_outputs)
                prob = tf.stack(prob)
            else:
                dec_cell = tf.contrib.rnn.LSTMBlockFusedCell(self.hidden_code_size)
                dec_outputs, dec_state = dec_cell(target_response, initial_state=enc_state, dtype=self.tf_type)
                de_outputs = None

        if target_response is None:
            de_embedded = tf.stack(de_outputs)
        else:
            de_embedded = tf.tensordot(dec_outputs, de_embed_w, axes=[[2], [0]]) + de_embed_b
            prob = de_embedded

        go_dropped = tf.slice(de_embedded, [0, 0, 0], tf.shape(de_embedded) - [0, 0, 1], name='response')
        core_variables = [
            de_embed_w.name,
            de_embed_b.name,
            enc_cell._kernel.name,
            enc_cell._bias.name,
            dec_cell._kernel.name,
            dec_cell._bias.name]

        intermediates = {
            'enc_state': enc_state,
            'de_embedded': de_embedded,
            'dec_outputs': dec_outputs,
            'prob': prob
        }
        return go_dropped, core_variables, intermediates

    @staticmethod
    def inference_model(model_path, hparams):
        inference_model = CallResponseModel(hparams)

        with open(join(model_path, 'variables.json'), mode='r') as f:
            core_variables = json.load(f)

        if hparams['float_type'] == 'float64':
            tf_type = tf.float64
            np_type = np.float64
        elif hparams['float_type'] == 'float32':
            tf_type = tf.float32
            np_type = np.float32
        else:
            raise ValueError()

        # load all checkpointed variables to convert them to float_type
        tf.reset_default_graph()
        with tf.Session() as sess:
            variables = {}
            variables_to_load = []
            for name, shape in core_variables.items():
                ref = tf.Variable(np.zeros(shape, dtype=np_type), name=name[:-2])
                variables[name] = ref
                variables_to_load.append(ref)

            saver = tf.train.Saver(variables_to_load)
            cp = tf.train.latest_checkpoint(model_path)
            saver.restore(sess, cp)

            variable_values = {}
            for name, var in variables.items():
                variable_values[name] = var.eval().astype(np_type)
        sess.close()
        tf.reset_default_graph()

        with tf.Session() as sess:
            call = tf.placeholder(
                dtype=tf_type,
                shape=(None, None, inference_model.encoder.encoding_channels),
                name='call')
            inference_model.core_graph(call, None)

            sess.run(tf.global_variables_initializer())
            for var in tf.global_variables():
                var.load(variable_values[var.name], session=sess)

            builder_path = join(model_path, 'inference_builder')
            try:
                shutil.rmtree(builder_path)
            except OSError as e:
                if e.errno == ENOENT:
                    pass
                else:
                    raise
            builder = SavedModelBuilder(join(model_path, 'inference_builder'))
            builder.add_meta_graph_and_variables(
                sess, [])
            builder.save()

        with open(join(model_path, 'inference_builder', 'encoder.json'), mode='w') as f:
            json.dump(hparams['encoder_dict'], f)

    def train(self, dataset_path, output_path, reset_learning_rate):
        try:
            with open(join(output_path, 'dataset.p'), mode='rb') as f:
                _LOGGER.debug('Loading dataset from file')
                dataset = pickle.load(f)
        except OSError as e:
            if e.errno == ENOENT:
                _LOGGER.debug('Building dataset from file')
                dataset = self.build_dataset(dataset_path)
                with open(join(output_path, 'dataset.p'), mode='wb') as f:
                    pickle.dump(dataset, f)
            else:
                raise

        training_params = {}
        for param in self._training_params:
            param_val = getattr(self, param)
            if param_val is None:
                raise ValueError(f'Key "{param}" not set in constructor, but is required to train the model.')

            training_params[param] = param_val

        with open(join(output_path, 'training_parameters.json'), mode='w') as f:
            json.dump(training_params, f)

        num_training_examples = dataset['training_indices'].size
        num_batches, remainder = divmod(num_training_examples, self.batch_size)
        if remainder != 0:
            raise ValueError(f'num of training examples ({num_training_examples}) must be an '
                             f'integer multiple of batch size ({self.batch_size})')

        try:
            tf.reset_default_graph()
            with tf.Session() as sess:
                tf.set_random_seed(self.seed)
                step = tf.train.get_or_create_global_step()

                calls = tf.constant(dataset['calls'], dtype=self.tf_type)

                response_samples, num_responses, response_chans = dataset['responses'].shape
                responses_with_go = np.empty((response_samples, num_responses, response_chans+1))
                responses_with_go[0, :, :] = 0
                responses_with_go[0, :, -1] = 1
                responses_with_go[1:, :, :-1] = dataset['responses'][:1, :, :]

                responses_with_go = tf.constant(responses_with_go, dtype=self.tf_type)
                responses = tf.constant(dataset['responses'], dtype=self.tf_type)

                learning_rate = tf.Variable(
                    self.learning_rate, dtype=self.tf_type, trainable=False, name='learning_rate')
                learning_rate_decrease_op = tf.assign(
                    learning_rate,
                    tf.multiply(tf.cast(_LR_MULTIPLIER, self.tf_type), learning_rate))

                keep_prob = tf.placeholder(dtype=self.tf_type, shape=[])

                batch_indices = tf.placeholder(dtype=tf.int32, shape=[self.batch_size])
                batch_calls = tf.gather(calls, batch_indices, axis=1)
                batch_responses = tf.gather(responses, batch_indices, axis=1)
                batch_responses_with_go = tf.gather(responses_with_go, batch_indices, axis=1)

                outputs, core_variables, _ = self.core_graph(batch_calls, batch_responses_with_go)

                core_variable_map = {}
                for name in core_variables:
                    cur_shape = sess.graph.get_tensor_by_name(name).shape
                    core_variable_map[name] = cur_shape.as_list()

                with open(join(output_path, 'variables.json'), mode='w') as f:
                    json.dump(core_variable_map, f)

                with tf.variable_scope('loss'):
                    cross_entropy = tf.nn.softmax_cross_entropy_with_logits_v2(
                        labels=batch_responses, logits=outputs, dim=2)
                    total_cross_entropy = tf.reduce_sum(cross_entropy)

                total_loss = total_cross_entropy

                def clip_grad(opt):
                    gradients, variables = zip(*opt.compute_gradients(total_loss))
                    gradients, _ = tf.clip_by_global_norm(gradients, self.gradient_clip)
                    return opt.apply_gradients(zip(gradients, variables), global_step=step)

                adam_optimizer = tf.train.AdamOptimizer(learning_rate)
                adam_step = clip_grad(adam_optimizer)
                # grad_optimizer = tf.train.GradientDescentOptimizer(learning_rate)
                # grad_step = clip_grad(grad_optimizer)

                epoch = tf.Variable(0, name='epoch', trainable=False, dtype=tf.int64)
                increment_epoch = tf.assign_add(epoch, 1)

                # valid_merged = tf.summary.scalar('validation_cross_entropy', total_cross_entropy)
                train_merged = tf.summary.scalar('training_cross_entropy', total_cross_entropy)

                min_loss = tf.Variable(np.inf, name='min_loss', trainable=False, dtype=self.tf_type)
                min_loss_epoch = tf.Variable(0, name='min_loss_epoch', trainable=False, dtype=tf.int64)
                update_cond = total_cross_entropy < min_loss

                new_min_loss = tf.cond(
                    update_cond,
                    lambda: total_cross_entropy,
                    lambda: min_loss
                )

                min_loss_updated = tf.cond(
                    update_cond,
                    lambda: 1,
                    lambda: 0
                )

                new_min_loss_epoch = tf.cond(
                    update_cond,
                    lambda: epoch,
                    lambda: min_loss_epoch
                )

                update_min_loss = tf.assign(min_loss, new_min_loss)
                update_min_loss_epoch = tf.assign(min_loss_epoch, new_min_loss_epoch)

                hyper_parameter_summary = tf.summary.merge([
                    tf.summary.scalar('learning_rate', learning_rate),
                    tf.summary.scalar('keep_prob', keep_prob),
                    tf.summary.scalar('min_loss', min_loss),
                    tf.summary.scalar('min_loss_epoch', min_loss_epoch)
                ])

                writer = tf.summary.FileWriter(output_path, graph=sess.graph)
                aux_variables = [epoch, min_loss, min_loss_epoch, learning_rate]
                saver = tf.train.Saver(tf.trainable_variables().extend(aux_variables))
                checkpoint = tf.train.latest_checkpoint(output_path)

                rewind_path = join(output_path, 'regression')
                rewind_saver = tf.train.Saver(tf.trainable_variables().extend(aux_variables))
                try:
                    mkdir(rewind_path)
                except OSError as e:
                    if e.errno == EEXIST:
                        pass
                    else:
                        raise

                if checkpoint is None:
                    _LOGGER.info(f'Initializing model in {output_path}')
                    initializer = tf.global_variables_initializer()
                    sess.run(initializer)
                    saver.save(sess, join(output_path, 'checkpoint'), write_meta_graph=True, global_step=epoch)
                else:
                    _LOGGER.info(f'Restoring model from {output_path}')

                    saver.restore(sess, checkpoint)

                if reset_learning_rate:
                    _LOGGER.info(f'Reseting learning rate to {self.learning_rate}')
                    learning_rate.load(self.learning_rate)

                while True:
                    epoch_n, = sess.run([epoch])

                    if epoch_n % 100 == 0:
                        feed = {keep_prob: 1}
                        cur_hp_summary, = sess.run([hyper_parameter_summary], feed_dict=feed)
                        writer.add_summary(cur_hp_summary, global_step=epoch_n)

                        feed = {batch_indices: dataset['training_indices'], keep_prob: 1}
                        summary, train_entropy, min_updated, min_loss_value, min_loss_epoch_value = sess.run([
                            train_merged,
                            total_cross_entropy,
                            min_loss_updated,
                            update_min_loss,
                            update_min_loss_epoch],
                            feed_dict=feed)
                        writer.add_summary(summary, global_step=epoch_n)

                        cur_learning_rate = sess.run(learning_rate)

                        _LOGGER.info(f'+++++++++++++++++')
                        _LOGGER.info(f'learning_rate: {cur_learning_rate}')
                        _LOGGER.info(f'epoch: {epoch_n}')
                        _LOGGER.info(f'training entropy: {train_entropy}')
                        _LOGGER.info(f'minimum loss: {min_loss_value}')
                        _LOGGER.info(f'minimum loss epoch: {min_loss_epoch_value}')

                        if min_updated:
                            rewind_saver.save(sess, join(rewind_path, 'checkpoint'),
                                              global_step=epoch, write_meta_graph=False)
                            _LOGGER.info(
                                f'New minimum validation loss of '
                                f'{min_loss_value} at epoch {min_loss_epoch_value}')

                        if epoch_n > 0:
                            if train_entropy > _LOSS_REGRESSION_MULTIPLIER*min_loss_value:
                                rewind_checkpoint = tf.train.latest_checkpoint(rewind_path)
                                _LOGGER.info(f'\nLoss regression. Restoring from {rewind_checkpoint}.')
                                rewind_saver.restore(sess, rewind_checkpoint)
                                learning_rate.load(cur_learning_rate)
                                _LOGGER.info(f'restored LR: {sess.run(learning_rate)}')
                                sess.run([learning_rate_decrease_op])
                                _LOGGER.info(f'updated LR: {sess.run(learning_rate)}')
                            elif epoch_n - min_loss_epoch_value > _STAGNATION_COUNT:
                                rewind_checkpoint = tf.train.latest_checkpoint(rewind_path)
                                _LOGGER.info(f'\nLoss stagnation. Restoring from {rewind_checkpoint}.')
                                rewind_saver.restore(sess, rewind_checkpoint)
                                learning_rate.load(cur_learning_rate)
                                _LOGGER.info(f'restored LR: {sess.run(learning_rate)}')
                                sess.run([learning_rate_decrease_op])
                                _LOGGER.info(f'updated LR: {sess.run(learning_rate)}')
                            else:
                                saver.save(
                                    sess, join(output_path, 'checkpoint'),
                                    write_meta_graph=False, global_step=epoch)

                    for batch_n in range(num_batches):
                        feed = {
                            batch_indices:
                                dataset['training_indices'][batch_n*self.batch_size:(batch_n+1)*self.batch_size],
                            keep_prob: self.keep_prob
                        }
                        sess.run(adam_step, feed_dict=feed)

                    sess.run([increment_epoch])
        except KeyboardInterrupt:
            CallResponseModel.inference_model(output_path, self.hparams)
            sys.exit(0)


class EvalModel:
    def __init__(self, builder_dir):

        _LOGGER.debug('Loading model')
        if tf.get_default_session() is not None:
            raise ValueError('Detected an existing session.')

        self.eval_session = tf.Session()
        atexit.register(self.eval_session.close)
        tf_loader.load(self.eval_session, [], builder_dir)
        self.call = self.eval_session.graph.get_tensor_by_name('call:0')
        self.response = self.eval_session.graph.get_tensor_by_name('response:0')

        with open(join(builder_dir, 'encoder.json'), mode='r') as f:
            encoder_dict = json.load(f)

        self.encoder = encoder_from_dict(encoder_dict)
        _LOGGER.debug('Model loaded')

    def evaluate(self, encoding):
        return self.eval_session.run(self.response, feed_dict={self.call: encoding})
