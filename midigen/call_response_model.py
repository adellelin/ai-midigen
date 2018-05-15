from os.path import join
from os import walk
import sys
import logging
import numpy as np
import tensorflow as tf
import pretty_midi as pm
from midigen.encode import encoder_from_dict

_LOGGER = logging.getLogger('CallResponseModel')


class CallResponseModel:
    def __init__(self, hparams):
        self.hparams = hparams
        self.encoder_dict = hparams['encoder_dict']
        self.hidden_code_size = hparams['hidden_code_size']
        self.batch_size = hparams['batch_size']
        self.float_type = hparams['float_type']
        if self.float_type == 'float64':
            self.tf_type = tf.float64
        elif self.float_type == 'float32':
            self.tf_type = tf.float32
        else:
            raise ValueError()

        self.seed = None
        self.validation_ratio = None
        self.learning_rate = None
        self.gradient_clip = None
        self.keep_prob = None

        optional_params = [
            'seed',
            'validation_ratio',
            'learning_rate',
            'gradient_clip',
            'keep_prob',
        ]

        for key in optional_params:
            try:
                setattr(self, key, hparams[key])
            except KeyError:
                pass

        self.encoder = encoder_from_dict(hparams['encoder_dict'])

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
            'calls': np.stack(calls),
            'responses': np.stack(responses),
            'training_indices': indices[:num_training_examples],
            'validation_indices': indices[num_training_examples:]
        }

        return dataset

    def core_graph(self, inputs, target_response):
        with tf.variable_scope('encoder', reuse=tf.AUTO_REUSE):
            cell = tf.nn.rnn_cell.BasicLSTMCell(self.hidden_code_size)
            if self.keep_prob != 1 and self.keep_prob is not None:
                cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=self.keep_prob)
            enc_outputs, enc_state = tf.nn.dynamic_rnn(
                cell, inputs, dtype=self.float_type)
            # enc_w, enc_b = cell.weights

        with tf.variable_scope('decoder', reuse=tf.AUTO_REUSE):
            de_embed_init = np.random.normal(
                loc=0, scale=np.sqrt(2.0/(self.hidden_code_size + self.encoder.encoding_channels + 1)),
                size=(self.hidden_code_size, self.encoder.encoding_channels + 1))
            de_embed_w = tf.Variable(de_embed_init, name='de_embed_w', trainable=True, dtype=self.tf_type)
            de_embed_b = tf.Variable(np.zeros(self.encoder.encoding_channels + 1), dtype=self.tf_type,
                                     name='de_embed_b', trainable=True)

            cell = tf.nn.rnn_cell.BasicLSTMCell(self.hidden_code_size)
            if self.keep_prob != 1 and self.keep_prob is not None:
                cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=self.keep_prob)

            # generate GO vector
            go_np = np.zeros((self.batch_size, self.encoder.encoding_channels + 1))
            go_np[:, -1] = 1
            go = tf.constant(go_np, dtype=self.tf_type)

            h_first, c_first = cell(go, enc_state)
            de_first = tf.add(tf.matmul(h_first, de_embed_w), de_embed_b, name='out0')
            dec_outputs = [de_first]
            dec_states = [c_first]
            num_time_steps = inputs.shape[1]
            for i in range(num_time_steps - 1):
                if target_response is None:
                    prev_prob = tf.nn.softmax(dec_outputs[-1], dim=1)
                    h_cur, state_cur = cell(prev_prob, dec_states[-1])
                else:
                    h_cur, state_cur = cell(target_response[:, i, :], dec_states[-1])

                de_cur = tf.add(tf.matmul(h_cur, de_embed_w), de_embed_b, name='out' + str(i + 1))
                dec_outputs.append(de_cur)
                dec_states.append(state_cur)
            dec_cat = tf.stack(dec_outputs, axis=1)

        return dec_cat

    def train(self, dataset, output_path):
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

                responses_with_go = np.concatenate(
                    (dataset['responses'],
                     np.zeros((dataset['responses'].shape[0], dataset['responses'].shape[1], 1))),
                    axis=2)
                responses = tf.constant(responses_with_go, dtype=self.tf_type)

                learning_rate = tf.placeholder(dtype=self.tf_type, shape=[])
                keep_prob = tf.placeholder(dtype=self.tf_type, shape=[])

                batch_indices = tf.placeholder(dtype=tf.int32, shape=[self.batch_size])
                batch_calls = tf.gather(calls, batch_indices, axis=0)
                batch_responses = tf.gather(responses, batch_indices, axis=0)

                outputs = self.core_graph(batch_calls, batch_responses)

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

                valid_merged = tf.summary.scalar('validation_cross_entropy', total_cross_entropy)
                train_merged = tf.summary.scalar('training_cross_entropy', total_cross_entropy)

                hyper_parameter_summary = tf.summary.merge([
                    tf.summary.scalar('learning_rate', learning_rate),
                    tf.summary.scalar('keep_prob', keep_prob)
                ])

                writer = tf.summary.FileWriter(output_path, graph=sess.graph)

                saver = tf.train.Saver(tf.trainable_variables().append(epoch))
                checkpoint = tf.train.latest_checkpoint(output_path)

                if checkpoint is None:
                    _LOGGER.info(f'Initializing model in {output_path}')
                    initializer = tf.global_variables_initializer()
                    sess.run(initializer)
                    saver.save(sess, join(output_path, 'checkpoint'), write_meta_graph=True, global_step=epoch)
                else:
                    _LOGGER.info(f'Restoring model from {output_path}')
                    saver.restore(sess, checkpoint)

                while True:
                    epoch_n, = sess.run([epoch])

                    if epoch_n % 100 == 0:
                        feed = {learning_rate: self.learning_rate,
                                keep_prob: self.keep_prob}
                        cur_hp_summary, = sess.run([hyper_parameter_summary], feed_dict=feed)
                        writer.add_summary(cur_hp_summary, global_step=epoch_n)

                        # TODO: get batch_indices to take an arbitrary number of indices instead of fixed at batch size
                        # feed = {batch_indices: dataset['validation_indices'], keep_prob: 1}
                        # summary, validation_entropy = sess.run([valid_merged, total_cross_entropy], feed_dict=feed)
                        # writer.add_summary(summary, global_step=epoch_n)

                        feed = {batch_indices: dataset['training_indices'], keep_prob: 1}
                        summary, train_entropy = sess.run([train_merged, total_cross_entropy], feed_dict=feed)
                        writer.add_summary(summary, global_step=epoch_n)
                        _LOGGER.info(f'+++++++++++++++++')
                        _LOGGER.info(f'learning_rate: {self.learning_rate}')
                        _LOGGER.info(f'epoch: {epoch_n}')
                        _LOGGER.info(f'training entropy: {train_entropy}')

                        # TODO: check for reversions and rewind
                        saver.save(sess, join(output_path, 'checkpoint'), write_meta_graph=False, global_step=epoch)

                        # TODO: build inference model

                    for batch_n in range(num_batches):
                        feed = {
                            batch_indices:
                                dataset['training_indices'][batch_n*self.batch_size:(batch_n+1)*self.batch_size],
                            learning_rate: self.learning_rate,
                            keep_prob: self.keep_prob
                        }
                        sess.run(adam_step, feed_dict=feed)

                    sess.run([increment_epoch])
        except KeyboardInterrupt:
            sys.exit(0)
