import argparse
from io import BytesIO
import base64
import logging
import sys
import traceback
import json
from os.path import join, expanduser
from flask import Flask, request, make_response
from flask_restful import Resource, Api
import numpy as np
import pretty_midi
try:
    import pymvnc as mvnc
except ImportError:
    mvnc = None
from midigen.call_response_model import EvalModel
from midigen.package import logger, version


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Launch generation server.')
    parser.add_argument('model_dir', help='exported model directory')
    parser.add_argument('--port', default=5000, help='http server port', type=int)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--verbose_response', action='store_true')
    parser.add_argument('--mvncs', action='store_true', help='use MvNCS for model backend')
    args = parser.parse_args()

    logger.debug('launching midigen server version: ' + version)

    if mvnc is None and args.mvncs:
        print('You must install pymvnc to use MvNCS as backend')
        exit(1)

    logger.debug('loading encoder')

    # Fire up the tensorflow session and recombobulate the generation graph
    if not args.mvncs:
        model = EvalModel(expanduser(args.model_dir))
    else:
        logger.debug('Connecting to MvNCS.')
        devs = mvnc.EnumerateDevices()
        if len(devs) == 0:
            print('No MvNCS found!')
            exit(1)

        # Find first free device (unfortunately no better way to do it with mvncapi)
        dev = None
        for d in devs:
            try:
                dev = mvnc.Device(d)
                dev.OpenDevice()
                break
            except:
                pass
        if dev is None:
            print('No free MvNCS found!')
            exit(1)

        logger.debug('Connected to MvNCS; allocating graph file')
        with open(join(args.model_dir, 'midigen.graph'), mode='rb') as f:
            graph_blob = f.read()
            graph = dev.AllocateGraph(graph_blob)
        logger.debug('Finished loading graph on MvNCS.')

    app = Flask(__name__)
    api = Api(app)

    class TFGen(Resource):
        # create prettymidi object, encodes it, evaluate it, decode output distribution into midi object
        # rest of it packs into format that http server
        def post(self):
            def error_response(e):
                logger.exception(e)
                e_type, e_value, e_traceback = sys.exc_info()
                e_traceback = traceback.format_tb(e_traceback)

                e_dict = {'error_type': str(e_type),
                          'error_value': str(e_value),
                          'error_traceback': ''.join(e_traceback)}
                error_json = json.dumps(e_dict, ensure_ascii=False).encode('utf8')
                error_response_value = make_response(error_json)
                error_response_value.headers['content-type'] = 'application/json; charset=utf-8'
                return error_response_value

            try:
                call_midi = pretty_midi.PrettyMIDI(request.stream)
            except EOFError as err:
                return error_response(err)

            try:
                call_encoded = model.encoder.encode(call_midi).reshape(
                    (model.encoder.num_time_steps, 1, model.encoder.num_symbols))
            except IndexError as err:
                return error_response(err)

            if not args.mvncs:
                # send encoding into model
                outputs_cat = model.evaluate(call_encoded)[:, 0]
            else:
                graph.LoadTensor(call_encoded.astype(np.float16), '')
                outputs_cur, _ = graph.GetResult()
                outputs_cat = np.array(outputs_cur, dtype=np.float32)

            # decode the response output
            response_midi = model.encoder.decode(outputs_cat)

            sio = BytesIO()
            response_midi.write(sio)
            a = sio.getvalue()
            a_b64 = base64.b64encode(a).decode()
            logger.debug('generated midi binary: ' + a_b64)
            if args.verbose_response:
                output_prob = outputs_cat[:, :]
                scale = 100.0
                output_prob_norm = np.exp(output_prob/scale)/np.sum(np.exp(output_prob/scale), axis=1)[:, np.newaxis]

                r_dict = {'midi': a_b64,
                          'output_distribution': output_prob_norm.tolist()}
                j = json.dumps(r_dict, ensure_ascii=False).encode('utf8')
                response = make_response(j)
                response.headers['content-type'] = 'application/json; charset=utf-8'
                return response
            else:
                r = make_response(a)
                r.headers['content-type'] = 'application/octet-stream'
                return r

    api.add_resource(TFGen, '/tfgen')

    app.run(port=args.port, host=args.host)


if __name__ == '__main__':
    main()
