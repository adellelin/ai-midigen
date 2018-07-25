import argparse
from os.path import expanduser, join
from os import mkdir
from errno import EEXIST
import pickle
import pretty_midi as pm
from midigen.call_response_model import EvalModel


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

    output_path = expanduser(args.output_path)
    try:
        mkdir(output_path)
    except OSError as e:
        if e.errno == EEXIST:
            pass
        else:
            raise

    # create the model, then load the validation set created at training side
    # run validation through model
    model = EvalModel(expanduser(args.model_path))
    with open(expanduser(args.dataset_path), mode='rb') as f:
        dataset = pickle.load(f)

    validation_calls = dataset['calls'][:, dataset['validation_indices'], :]
    validation_responses = model.evaluate(validation_calls)

    training_calls = dataset['calls'][:, dataset['training_indices'], :]
    training_responses = model.evaluate(training_calls)

    call_program = pm.instrument_name_to_program('Acoustic Grand Piano')
    response_program = pm.instrument_name_to_program('Electric Grand Piano')

    def build_midi(call, response, filename_prefix):
        midis = []
        for example_n in range(call.shape[1]):
            cur_call = call[:, example_n]
            cur_call_mid = model.encoder.decode(cur_call, program=call_program)
            cur_call_mid.write(join(output_path, f'{filename_prefix}_call_{example_n}.mid'))
            midis.append(cur_call_mid)

            cur_response = response[:, example_n]
            cur_response_mid = model.encoder.decode(cur_response, program=response_program)
            cur_response_mid.write(join(output_path, f'{filename_prefix}_response_{example_n}.mid'))
            midis.append(cur_response_mid)

        return concat(midis, args.min_len)

    validation_track_path = join(output_path, 'validation.mid')
    build_midi(validation_calls, validation_responses, 'validation').write(validation_track_path)

    full_set_path = join(output_path, 'full_set.mid')
    build_midi(dataset['calls'], dataset['responses'], 'full').write(full_set_path)

    training_track_path = join(output_path, 'training.mid')
    build_midi(training_calls, training_responses, 'training').write(training_track_path)

    try:
        call_fnames = dataset['call_fnames']
    except KeyError:
        pass
    else:
        with open(join(output_path, 'valid_call_fnames.csv'), mode='w') as f:
            for idx in dataset['validation_indices']:
                fname = call_fnames[idx]
                f.write(fname+'\n')


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


if __name__ == '__main__':
    main()
