import atexit
import argparse
from io import BytesIO
import base64
import logging
import sys
import traceback
import json
from os.path import join
from flask import Flask, request, make_response
from flask_restful import Resource, Api
import tensorflow as tf
from tensorflow.python.saved_model import loader as tf_loader
import numpy as np
import pretty_midi
from midigen.encode import encoder_from_dict
from midigen.package import logger, version


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Launch generation server.')
    parser.add_argument('model_dir', help='exported model directory')
    parser.add_argument('--port', default=5000, help='http server port', type=int)
    parser.add_argument('--verbose_response', action='store_true')
    args = parser.parse_args()

    logger.debug('launching midigen server version: ' + version)
    # Fire up the tensorflow session and recombobulate the generation graph
    logger.debug('Loading tensorflow model.')
    sess = tf.Session()
    atexit.register(sess.close)
    tf_loader.load(sess, [], args.model_dir)
    logger.debug('Finished loading tensorflow model.')

    logger.debug('loading encoder')
    with open(join(args.model_dir, 'encoder.json'), mode='r') as f:
        encoder = encoder_from_dict(json.load(f))

    outputs = []
    for i in range(encoder.num_time_steps):
        outputs.append(sess.graph.get_tensor_by_name('decoder/out'+str(i)+':0'))
    call_ohcs = sess.graph.get_tensor_by_name('call_ohcs:0')

    app = Flask(__name__)
    api = Api(app)

    class TFGen(Resource):
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
                call_encoded = encoder.encode(call_midi).reshape((1, encoder.num_time_steps, encoder.num_symbols))
            except IndexError as err:
                return error_response(err)

            outputs_cur = sess.run(outputs, feed_dict={call_ohcs: call_encoded})
            outputs_cat = np.array(outputs_cur, dtype=np.float32)
            response_midi = encoder.decode(outputs_cat)

            sio = BytesIO()
            response_midi.write(sio)
            a = sio.getvalue()
            a_b64 = base64.b64encode(a).decode()
            logger.debug('generated midi binary: ' + a_b64)
            if args.verbose_response:
                output_prob = outputs_cat[:, 0, :]
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

    app.run(port=args.port)


if __name__ == '__main__':
    main()
