import argparse
from os.path import expanduser, join
from os import walk
import pickle
import pretty_midi as pm
import numpy as np
from midigen.call_response_model import EvalModel, CallResponseModel
from midigen.encode import MelodyEncoder


def main():
    parser = argparse.ArgumentParser('Generate validation response tracks from a trained call/response model')
    parser.add_argument(
        'dataset_path', help='path to the pickled dataset')
    parser.add_argument(
        'model_path', help='path to model builder')
    parser.add_argument(
        'output_path', help='path to output the results')
    parser.add_argument('min_len', help='minimum length', type=float)

    args = parser.parse_args()
    # create the model, then load the validation set created at training side
    # run validation through model
    model = EvalModel(expanduser(args.model_path))


    # build dataset
    print(args.dataset_path)
    dataset = build_dataset(args.dataset_path, model)

    #validation_calls = dataset['calls'][:, dataset['validation_indices'], :]
    #validation_responses = model.evaluate(validation_calls)

    print( dataset['training_indices'])

    training_calls = dataset['calls'][:, dataset['training_indices'], :]
    #print("training calls", training_calls)
    training_responses = model.evaluate(training_calls)

    call_program = pm.instrument_name_to_program('Acoustic Grand Piano')
    response_program = pm.instrument_name_to_program('Electric Grand Piano')

    def build_midi(call, response):
        midis = []
        for example_n in range(call.shape[1]):
            cur_call = call[:, example_n]
            midis.append(model.encoder.decode(cur_call, program=call_program))
            cur_response = response[:, example_n]
            midis.append(model.encoder.decode(cur_response, program=response_program))
        return concat(midis, args.min_len)

    full_set_path = join(expanduser(args.output_path), 'full_set.mid')
    build_midi(dataset['calls'], dataset['responses']).write(full_set_path)

    #validation_track_path = join(expanduser(args.output_path), 'validation.mid')
    #build_midi(validation_calls, validation_responses).write(validation_track_path)

    training_track_path = join(expanduser(args.output_path), 'training.mid')
    build_midi(training_calls, training_responses).write(training_track_path)



def concat(midis, min_len=None):
    """
    Concatenate notes in time from  a list of pretty midi objects
    :param midis: an iterable of midis
    :param min_len: the minimum length of each segment
    :return: a pretty_midi midi object
    """
    midi = pm.PrettyMIDI()
    prev_end_time = 0.0
    new_insts = {}

    for cur_midi in midis:
        cur_end_time = 0.0
        for inst in cur_midi.instruments:
            if inst.program not in new_insts.keys():
                new_insts[inst.program] = pm.Instrument(program=inst.program)
            for note in inst.notes:
                new_note = pm.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=note.start + prev_end_time,
                    end=note.end + prev_end_time)

                new_insts[inst.program].notes.append(new_note)
                cur_end_time = max(cur_end_time, new_note.end)

        if min_len is None:
            prev_end_time = cur_end_time
        else:
            prev_end_time = max(cur_end_time, prev_end_time + min_len)

    for new_inst in new_insts.values():
        midi.instruments.append(new_inst)

    return midi


def build_dataset(data_dir, model):

    np.random.seed(1)

    calls = []
    responses = []

    for dirName, subdirList, fileList in walk(data_dir):
        cur_cr = {}
        for fname in fileList:
            if fname.endswith('.mid') and not fname[0] == '.':
                try:
                    num = int(fname.replace('.mid', '').replace(' ', '_').split('_')[-1])
                except ValueError:
                    print(f'file name does not end with integer {fname}')
                    continue

                full_path = join(dirName, fname)
                try:
                    midi = pm.PrettyMIDI(full_path)
                    assert len(midi.instruments[0].notes) > 3
                    cur_cr[num] = model.encoder.encode(midi, instrument_index=0)
                    #print("encode", cur_cr[num])
                except (AssertionError, IOError, KeyError):
                    print(f'Could not add midi file {join(dirName, fname)}.')

        for k in cur_cr.keys():
            if k % 2 == 1:
                try:
                    cur_call = cur_cr[k]
                    cur_response = cur_cr[k + 1]
                    responses.append(cur_response)
                    calls.append(cur_call)
                    #print("calls", calls)
                except KeyError:
                    print(f'Could not add index {k} from {dirName} because '
                                    f'it does not have a valid call/response.')

    print(f'building dataset from {data_dir}')

    call_len = calls[0].shape[0]
    print("len", call_len)
    for call, response in zip(calls, responses):
        assert call.shape[0] == call_len
        assert response.shape[0] == call_len

    num_examples = len(calls)
    print(num_examples)
    validation_ratio = 0  # use all midi's for evaluation
    num_training_examples = int(num_examples*(1.0-validation_ratio))
    indices = np.arange(num_examples, dtype=np.int32)
    #np.random.shuffle(indices)

    dataset = {
        'calls': np.swapaxes(np.stack(calls), 0, 1),
        'responses': np.swapaxes(np.stack(responses), 0, 1),
        'training_indices': indices[:num_training_examples],
        'validation_indices': indices[num_training_examples:]
    }

    return dataset


if __name__ == '__main__':
    main()
