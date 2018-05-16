import argparse
from sys import executable
from collections import namedtuple
import logging
from logging.handlers import RotatingFileHandler
import time
from io import BytesIO
from os import path, makedirs, listdir, remove
from shutil import rmtree
from errno import EEXIST, ENOTDIR
import atexit
import requests
import mido
import pretty_midi as pm
from appdirs import AppDirs
import pykka
from midigen.package import version

import json
import base64
import numpy as np
import sys

from pythonosc import osc_message_builder
from pythonosc import osc_bundle_builder
from pythonosc import udp_client

# define constants
_bars_per_call = 2
_seconds_per_bar = 2
_seconds_per_call = _bars_per_call * _seconds_per_bar


# class GenPlayActor(pykka.ThreadingActor):
class GenPlayActor():
    def __init__(self, outport, log_midi_files, logdir, crserver_url, logger, tempo):
        # super(GenPlayActor, self).__init__()
        self._response_midi = None

        self._outport = outport
        self._crserver_url = crserver_url
        self._logger = logger

        self._log_midi_files = log_midi_files
        self._midi_file_log_index = 0
        self._max_midi_files = 100
        self._logdir = logdir
        self._tempo = tempo
        #self._is_last_bar = is_last_bar

    # def on_receive(self, message):
    def tell(self, message, osc_client):
        # generate a post to send to call response server
        if message['command'] == 'generate':
            gen_start = time.time()
            midi = message['midi']
            inport = message['inport']
            responses_dir = message['responses_dir']
            client = osc_client
            if self._log_midi_files:
                call_path = path.join(self._logdir, 'call'+str(self._midi_file_log_index)+'.mid')
                midi.write(call_path)

            # write call as binary
            call_io = BytesIO()
            midi.write(call_io)
            a = call_io.getvalue()

            # post request to server
            try:
                r = requests.post(
                    url=self._crserver_url,
                    data=a,
                    headers={'Content-Type': 'application/octet-stream'})

                # set the return type options
                return_type=['application/json; charset=utf-8','application/octet-stream']

                # clear visuals
                client.send_message("/response_reset/", 1)

            except requests.ConnectionError:
                logging.error("cr server not found")
                sys.exit(-1)

            try:
                assert r.headers['content-type'] in return_type

                # parse the content with probability distribution
                if r.headers['content-type'] == 'application/json; charset=utf-8':
                    print("probability and midi", r.headers['content-type'])

                    response_dict = json.loads(r.content, encoding='utf-8')
                    response_midi_bytes = base64.b64decode(response_dict['midi'])
                    response_io = BytesIO(response_midi_bytes)
                    response_io.seek(0)
                    response_out_dist = response_dict['output_distribution']
                    response_out_np_dist = np.array(response_out_dist)
                    out_symbols = np.argmax(response_out_np_dist, axis=1)
                    out_symbols = out_symbols.tolist()
                    client.send_message("/output_symbols/", out_symbols)
                    client.send_message("/animation/seq", 1)  # trigger rnn animation

                    try:
                        self.write_output_midi(response_io, responses_dir)
                        response_out_np_dist = np.array(response_out_dist, dtype=float)
                        # set up osc bundle
                        bundle = osc_bundle_builder.OscBundleBuilder(
                            osc_bundle_builder.IMMEDIATELY)
                        test_array = []
                        for index in range(len(response_out_np_dist)):
                            sub_array = []
                            msg = osc_message_builder.OscMessageBuilder(address="/probdist/" + str(index))
                            for x in np.nditer(response_out_np_dist[index]):
                                msg.add_arg(float(x)*2)
                                sub_array.append(float(x))
                            bundle.add_content(msg.build())
                            test_array.append(sub_array)
                            # print("array", index, sub_array)
                        bundle = bundle.build()
                        client.send(bundle)
                        try:
                            assert test_array[index] == response_out_dist[index]
                        except AssertionError:
                            logging.warning("arrays don't match")
                    except IOError as e:
                        logging.warning("error")
                    else:
                        self._logger.debug('cr round trip: ' + str(time.time()-gen_start))

            except AssertionError as e:
                self._logger.exception(e)
                self._logger.error(r.headers['content-type'])
                self._response_midi = None

            else:
                if r.headers['content-type'] == 'application/octet-stream':
                    response_io = BytesIO(r.content)
                    response_io.seek(0)
                    try:
                        self.write_output_midi(response_io, responses_dir)
                        print("output is midi")
                    except IOError as e:
                        self._logger.exception(e)
                    else:
                        self._logger.debug('cr round trip: ' + str(time.time()-gen_start))

        elif message['command'] == 'play':
            is_last_bar = message['is_last_bar']
            if self._response_midi is not None:
                totalMessages = ([len(track) for track in self._response_midi.tracks][1])

            try:
                msgCount = 1
                if self._response_midi is not None:
                    for play_msg in self._response_midi.play():
                        #print("tracks", self._response_midi.tracks, len(self._response_midi.tracks))
                        #print("tracks print", self._response_midi.print_tracks())
                        self._outport.send(play_msg)
                        #print("message Count", msgCount, play_msg)
                        # send last note message for flourish to avatars
                        if is_last_bar == True and msgCount > (totalMessages - 3) and play_msg.velocity > 0:
                            last_note_msg = mido.Message(type='control_change', control=22, value=127)
                            self._outport.send(last_note_msg)

                        msgCount = msgCount + 1
                    self._response_midi = None
            except AttributeError as e:
                self._logger.exception(e)
        else:
            self._logger.error('Actor received unknown message: ' + str(message))

    def write_output_midi(self, response_io, responses_dir):
        self._response_midi = mido.MidiFile(file=response_io)
        print("response midi", response_io)
        self._response_midi.type = 0
        self._response_midi.ticks_per_beat = self._tempo

        if self._log_midi_files:
            response_path = path.join(self._logdir, 'response' + str(self._midi_file_log_index) + '.mid')
            with open(response_path, mode='wb') as f:
                response_io.seek(0)
                f.write(response_io.getvalue())
            # if str(inport) == "<open input 'AI_Bass_In' (RtMidi/MACOSX_CORE)>":
            loop_response_path = responses_dir
            with open(loop_response_path, mode='wb') as loop:
                response_io.seek(0)
                loop.write(response_io.getvalue())
                print("midi file", loop_response_path)
            self._midi_file_log_index = (self._midi_file_log_index + 1) % self._max_midi_files


def main():
    parser = argparse.ArgumentParser(description='Launch generation server.')
    parser.add_argument('crserver_url', help='exported model directory')
    parser.add_argument('responses_dir', help='where the loop midi file goes')
    parser.add_argument('--in_port', default='AI_Guitar_In', help='Port from max')
    parser.add_argument('--out_port', default='AI_Guitar_Out', help='Port to max')
    parser.add_argument('--log_midi_files', action='store_true',
                        help='Flag to turn on midi file logging')
    parser.add_argument('--call_padding_time', default=0.0625, type=float)
    parser.add_argument('--tempo', default=226, type=int, help='Changes playback tempo')


    # osc setup
    parser.add_argument("--ip", default="127.0.0.1",
                        help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5008,
                        help="The port the OSC server is listening on")
    args = parser.parse_args()
    osc_client = udp_client.SimpleUDPClient(args.ip, args.port)

    args = parser.parse_args()

    # create and clear log directory
    dirs = AppDirs('rt_midi_interface', 'midigen', version=version)
    logdir = path.join(dirs.user_log_dir, args.in_port+'_'+args.out_port)
    try:
        makedirs(logdir)
    except OSError as e:
        if e.errno != EEXIST:
            raise
    for filename in listdir(logdir):
        filepath = path.join(logdir, filename)
        try:
            rmtree(filepath)
        except OSError as e:
            if e.errno != ENOTDIR:
                raise
            else:
                remove(filepath)

    # create logger
    log_file = path.join(logdir, 'log')
    logger = logging.getLogger('rt_midi_interface')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.DEBUG)
    # create file log handler
    fh = RotatingFileHandler(log_file, maxBytes=1e5, backupCount=100)
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    # create console log handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    ch.setLevel(logging.INFO)

    logger.info('Starting rt_midi_interface version:\n    ' + version)
    logger.info('Script path:\n    ' + __file__)
    logger.debug('Python executable:\n    ' + executable)
    logger.info('Log directory:\n    ' + logdir)

    in_port = mido.open_input(args.in_port)
    out_port = mido.open_output(args.out_port)
    logger.info('In port: ' + str(in_port) + ' Out port: ' + str(out_port))
    is_last_bar = False;

    # initiate generation/play actor
    # actor = GenPlayActor.start(
    actor = GenPlayActor(
        outport=out_port, log_midi_files=args.log_midi_files, logdir=logdir,
        crserver_url=args.crserver_url, logger=logger, tempo=args.tempo)
    # atexit.register(actor.stop)

    # define state
    # counter that keeps track of current bar length
    bar_count = 0
    model_idle = True
    last_response_length_state = 2
    # current state of call bar length, updated through messages value attached to control messages
    call_bars = 2
    # time stamp of the most recent metronome tick
    most_recent_metronome = 0
    # buffer to hold previous max_buffer_time worth of notes
    max_buffer_time = 2 * _seconds_per_bar * 8 + 1
    note_buffer = []
    # define representation to store notes in note_buffer until conversion to midi
    Note = namedtuple(
        'Note',
        ['channel', 'pitch', 'velocity', 'start_time', 'end_time'])

    # dict to track key presses and releases
    on_notes = {}

    # enter control loop: reading messages from the input port
    for msg in in_port:
        msg_received = time.time()
        logger.debug('received message:\n    ' + str(msg) + '\n    at ' + str(msg_received))

        # prune old entries from note_buffer
        n = 0
        while len(note_buffer) > 0 and n < len(note_buffer):
            if msg_received - note_buffer[n].start_time > max_buffer_time:
                logger.debug('removing note From buffer: \n    ' + str(note_buffer[n]))
                del note_buffer[n]
            else:
                n += 1

        if msg.type == 'note_on':
            pitch = msg.note
            channel = msg.channel
            velocity = msg.velocity
            note_state = on_notes.pop((channel, pitch), None)
            if note_state is None and velocity != 0:
                # key pressed - add state to on_notes dict
                on_notes[(channel, pitch)] = (velocity, msg_received)
            elif note_state is not None and velocity == 0:
                # key released - add note to note buffer
                cur_note = Note(
                    channel=channel,
                    pitch=pitch,
                    velocity=note_state[0],
                    start_time=note_state[1],
                    end_time=msg_received)
                note_buffer.append(cur_note)
                logger.info('added note to buffer: \n    ' + str(cur_note))
            else:
                logger.error('Key press state error. Dropped a message?')
        elif msg.type == 'control_change' and msg.control == 20:
            value = msg.value

            if value not in [2, 4, 8, 12]:
            #if value not in [0, 1, 2]:
                logger.error('Unknown control_change message:\n    ' + str(msg))
                continue
            else:
                response_length_state = value
            most_recent_metronome = msg_received

            if response_length_state != last_response_length_state and model_idle is False:
                bar_count = 0
                model_idle = True
                last_response_length_state = response_length_state
                continue

            last_response_length_state = response_length_state

            # if model is idle, check to see if a note has been played in the previous bar
            #  if not, continue without incrementing bar counter
            #  if so, set bar counter to zero and continue with normal operation
            if model_idle is True:
                # check to see if note has been played in previous bar
                notes_in_previous_bar = False
                for note in note_buffer:
                    bar_start_time = msg_received - _seconds_per_bar - args.call_padding_time
                    if note.start_time > bar_start_time:
                        notes_in_previous_bar = True

                # if no notes, stay idle and report ready state to max display
                if notes_in_previous_bar is False:
                    ready_msg = mido.Message(type='control_change', control=15, value=127)
                    out_port.send(ready_msg)
                    logger.info('idle')
                    continue
                else:
                    # leave idle state and set bar count to the beginning of the cycle
                    bar_count = 0
                    model_idle = False

            # bar_multiple = 1 + value**2
            # bars_per_cycle = 2 * _bars_per_call * bar_multiple
            #
            # call_bars = _bars_per_call * bar_multiple

            bars_per_cycle = 2 * value
            call_bars = value
            print ("bars_per_cyle", bars_per_cycle, "call_bars", call_bars)

            # increment and report bar count
            bar_count = (bar_count + 1) % bars_per_cycle
            logger.info("bar count: " + str(bar_count))
            bar_count_msg = mido.Message(type='control_change', control=20, value=bar_count)
            out_port.send(bar_count_msg)

            # update listening/playing state for max display
            if bar_count == 0:
                ready_msg = mido.Message(type='control_change', control=15, value=127)
                out_port.send(ready_msg)
            if bar_count == 1:
                listening_msg = mido.Message(type='control_change', control=16, value=127)
                out_port.send(listening_msg)
            elif bar_count == call_bars:
                playing_msg = mido.Message(type='control_change', control=17, value=127)
                out_port.send(playing_msg)

            # do real time playing of saved midi file at the start of the response cycle
            if bar_count >= call_bars and bar_count % _bars_per_call == 0:
                logger.info('trigger playback at: ' + str(msg_received))
                # send last bar state true on 2, 6, 14 bars otherwise false
                is_last_bar = bar_count == bars_per_cycle - 2
                actor.tell({'command': 'play', 'is_last_bar': is_last_bar}, osc_client)
            # if bar count is in the last bar of response phrase

        # my_actor_ref.tell({'command': 'generate'})
        # my_actor_ref.stop()

        elif msg.type == 'control_change' and msg.control == 21  and msg.value == 5:

            trigger_generation = call_bars - 1 <= bar_count < 2*call_bars - 1 and \
                                 bar_count % _bars_per_call == _bars_per_call - 1
            if not trigger_generation:
                continue

            generation_delta = msg_received - most_recent_metronome
            call_start_time = msg_received - (call_bars - 1) * _seconds_per_bar - generation_delta
            call_end_time = call_start_time + _seconds_per_call

            # convert a sequence of notes _seconds_per_call long, starting at call_start_time
            inst = pm.Instrument(program=0)
            for note in note_buffer:
                if note.start_time > call_start_time-args.call_padding_time and \
                        note.end_time < call_end_time + args.call_padding_time:

                    start_time = max(0, note.start_time-call_start_time)
                    note_len = note.end_time - note.start_time

                    pmnote = pm.Note(
                        velocity=note.velocity,
                        pitch=note.pitch,
                        start=start_time,
                        end=start_time + note_len)
                    inst.notes.append(pmnote)

            if len(inst.notes) == 0:
                logger.info('entering idle mode')
                model_idle = True
                bar_count = 0
            else:
                logger.info('generation triggered ' + str(_seconds_per_bar - generation_delta) + ' early')

                midi = pm.PrettyMIDI()
                midi.instruments.append(inst)
                actor.tell({'command': 'generate', 'midi': midi, 'inport':in_port,
                            'responses_dir': args.responses_dir}, osc_client)

        else:
            logger.error('Unknown message type: ' + str(msg))

if __name__ == '__main__':
    main()
