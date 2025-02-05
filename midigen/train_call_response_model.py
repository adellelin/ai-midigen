from os.path import expanduser, exists
from os import mkdir
import argparse
import json
import logging
from midigen.call_response_model import CallResponseModel


def main():
    parser = argparse.ArgumentParser('Train a call/response model')
    parser.add_argument(
        'dataset_path', help='path to the dataset')
    parser.add_argument(
        'output_path', help='path to output results')
    parser.add_argument(
        'encoder_path', help='path to a serialized encoder')
    parser.add_argument(
        '--hidden_code_size', type=int, help='size of the latent encoding', required=True)
    parser.add_argument(
        '--max_response_length', type=int, help='maximum length of response', required=True)
    parser.add_argument(
        '--batch_size', type=int, help='batch size used for training', required=True)
    parser.add_argument(
        '--float_type', help='precision used for training', choices=['float32', 'float64'], required=True)
    parser.add_argument(
        '--validation_ratio', help='ratio of examples to hold out for validation', type=float, required=True)
    parser.add_argument(
        '--gradient_clip', help='gradient clip', type=float, required=True)
    parser.add_argument(
        '--learning_rate', help='learning rate', type=float, required=True)
    parser.add_argument(
        '--keep_prob', help='dropout keep probability', type=float, required=True)
    parser.add_argument(
        '--seed', help='RNG seed', type=int, required=True)
    parser.add_argument(
        '--reset_learning_rate', action='store_true', help='reset learning rate to initial value'
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    with open(expanduser(args.encoder_path)) as f:
        encoder_dict = json.load(f)

    params = {
        'encoder_dict': encoder_dict,
        'hidden_code_size': args.hidden_code_size,
        'max_response_length': args.max_response_length,
        'batch_size': args.batch_size,
        'float_type': args.float_type,
        'validation_ratio': args.validation_ratio,
        'gradient_clip': args.gradient_clip,
        'learning_rate': args.learning_rate,
        'keep_prob': args.keep_prob,
        'seed': args.seed
    }

    output_fullpath = expanduser(args.output_path)

    if exists(output_fullpath) is False:
        mkdir(output_fullpath)
        mkdir(output_fullpath+"/inference_builder")

    model = CallResponseModel(params)
    model.train(expanduser(args.dataset_path), expanduser(output_fullpath), args.reset_learning_rate)


if __name__ == '__main__':
    main()
