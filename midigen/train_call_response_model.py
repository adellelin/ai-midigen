from os.path import expanduser
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

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    with open(expanduser(args.encoder_path)) as f:
        encoder_dict = json.load(f)

    params = {
        'encoder_dict': encoder_dict,
        'hidden_code_size': args.hidden_code_size,
        'batch_size': args.batch_size,
        'float_type': args.float_type,
        'validation_ratio': args.validation_ratio,
        'gradient_clip': args.gradient_clip,
        'learning_rate': args.learning_rate,
        'keep_prob': args.keep_prob,
        'seed': args.seed
    }

    model = CallResponseModel(params)
    dataset = model.build_dataset(expanduser(args.dataset_path))
    model.train(dataset, expanduser(args.output_path))


if __name__ == '__main__':
    main()
