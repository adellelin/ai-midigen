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
from mido.midifiles import midifiles
import pretty_midi as pm
from appdirs import AppDirs
import pykka
from midigen.package import version

# for visualizer
import json
import base64
import numpy as np
import sys
import math
from os.path import join
from midigen.encode import encoder_from_dict

from pythonosc import osc_message_builder
from pythonosc import osc_bundle_builder
from pythonosc import udp_client


# class GenPlayActor(pykka.ThreadingActor):
class OscSendActor():
    def __init__(self):
        pass

    def tell(self, message):
        if message['command'] == 'send_prob_dist':
            #logging.info("told to : ", message)

            response_out_dist = message['response_out_dist']
            out_symbols = message['out_symbols']
            client = message['osc_client']
            #is_guitar = message['is_guitar']
            visualizer_pitches = message['visualizer_pitches']

            # print("output distribution", response_out_np_dist)
            print("output symbols", out_symbols)

            # remap output symbols to the visualizer range
            print("visualizer ", visualizer_pitches)
            response_indeces = []
            selected_indeces = []

            # check the responses against the seleced visualizer pitch index
            for note in out_symbols:
                for k, v in visualizer_pitches.items():
                    if note == v:
                        response_indeces.append(k)

            client.send_message("/output_symbols/", response_indeces)

            # get the values in the visualizer pitches in an array to use as column lookup in the prob dist
            for k, v in visualizer_pitches.items():
                selected_indeces.append(v)
            print("out", selected_indeces, response_indeces)
            # self._logger.info("is visualizing" + str(is_visualizing))

            try:
                response_out_np_dist = np.array(response_out_dist, dtype=float)
                intensity_multiplier = 10

                # set up osc bundle
                bundle = osc_bundle_builder.OscBundleBuilder(
                    osc_bundle_builder.IMMEDIATELY)
                test_array = []

                # go through the time slices
                for i in range(response_out_np_dist.shape[0]):
                    sub_array = []
                    msg = osc_message_builder.OscMessageBuilder(address="/probdist/" + str(i))
                    # go throught the notes in the encoder indexed notes
                    for max_column_index in range(len(selected_indeces)):

                        probability = response_out_np_dist[i, selected_indeces[max_column_index]]
                        msg.add_arg(float(probability) * intensity_multiplier)
                        sub_array.append(float(probability))

                    #print(i, sub_array.index(max(sub_array)), sub_array)
                    bundle.add_content(msg.build())
                    test_array.append(sub_array)
                    #print("osc message prob", msg.address, msg.args)
                bundle = bundle.build()
                client.send(bundle)

                try:
                    assert test_array[i] == response_out_dist[i]
                except AssertionError:
                    logging.warning("arrays don't match")
            except IOError as e:
                print("error", e)

        pass

class BarCountActor():
    def __init__(self, outport):
        self._outport = outport

    def tell(self, message):
        if message['command'] == 'sendbarcount':
            bar_count = message['bar_count']
            #barcountmsg = mido.Message(type='control_change', control=22, value=self._bar_count_msg)
            bar_count_msg = mido.Message(type='control_change', control=20, value=bar_count)
            print("outport", self._outport, bar_count)
            self._outport.send(bar_count_msg)


class GenPlayActor(pykka.ThreadingActor):
#class GenPlayActor():
    def __init__(self, outport, log_midi_files, logdir, crserver_url, logger, tempo):
        super(GenPlayActor, self).__init__()
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

    def on_receive(self, message):
    #def tell(self, message):
        if message['command'] == 'generate':
            gen_start = time.time()
            midi = message['midi']
            inport = message['inport']
            responses_dir = message['responses_dir']
            is_visualizing = message['is_visualizing']
            client = message['osc_client']
            oscSendActor = message['oscSendActor']
            visualizer_pitches = message['visualizer_pitches']

            if self._log_midi_files:
                call_path = path.join(self._logdir, 'call'+str(self._midi_file_log_index)+'.mid')
                midi.write(call_path)

            # write call input as binary
            call_io = BytesIO()
            midi.write(call_io)
            a = call_io.getvalue()

            # post request to server
            try:
                r = requests.post(
                    url=self._crserver_url,
                    data=a,
                    headers={'Content-Type': 'application/octet-stream'})
                if is_visualizing is True:
                    # start nn animation visuals
                    client.send_message("/animation/seq", 1)  # trigger rnn animation
                else:
                    pass
                # set the return type options
                return_type=['application/json; charset=utf-8','application/octet-stream']

            except requests.ConnectionError:
                logging.error("cr server not found")
                sys.exit(-1)

            try:
                assert r.headers['content-type'] in return_type

                # parse the content with probability distribution
                if r.headers['content-type'] == 'application/json; charset=utf-8':
                    print("probability and midi", r.headers['content-type'])
                    response_dict = json.loads(r.content, encoding='utf-8')
                    try:
                        response_midi_bytes = base64.b64decode(response_dict['midi'])
                    except KeyError:
                        logging.error("key error from crserver invalid response")
                        return
                    response_io = BytesIO(response_midi_bytes)
                    response_io.seek(0)
                    self.write_output_midi(response_io, responses_dir)

                    if is_visualizing is True:
                        response_out_dist = response_dict['output_distribution']
                        response_out_np_dist = np.array(response_out_dist)
                        out_symbols = np.argmax(response_out_np_dist, axis=1)
                        out_symbols = out_symbols.tolist()
                        oscSendActor.tell({'command': 'send_prob_dist', 'response_out_dist': response_out_dist, 'out_symbols': out_symbols,
                                          'osc_client': client, 'visualizer_pitches': visualizer_pitches})


                # if in non-verbose, content is only midi file
                elif r.headers['content-type'] == 'application/octet-stream':
                    response_io = BytesIO(r.content)
                    response_io.seek(0)
                    try:
                        self.write_output_midi(response_io, responses_dir)
                    except IOError as e:
                        self._logger.exception(e)
                    else:
                        self._logger.debug('cr round trip: ' + str(time.time()-gen_start))

            except AssertionError as e:
                self._logger.exception(e)
                self._logger.error(r.headers['content-type'])
                self._response_midi = None


        elif message['command'] == 'play':
            #print("getting into play", self._response_midi)
            is_last_bar = message['is_last_bar']
            #print("is last bar in play", is_last_bar)
            ## get number of messages in response
            if self._response_midi is not None:
                totalMessages = ([len(track) for track in self._response_midi.tracks][1])
                #print(totalMessages, "total")
            try:
                msgCount = 1
                if self._response_midi is not None:
                    for play_msg in self._response_midi.play():
                        #print("tracks", self._response_midi.tracks, len(self._response_midi.tracks))
                        #print("tracks print", self._response_midi.print_tracks())
                        self._outport.send(play_msg)
                        print("Playing Note ", msgCount, play_msg)
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
    parser.add_argument("--json", default="/Users/adelleli/Documents/encoder.json", help = "location of json")
    parser.add_argument("--visualizer_notes", default=[0, 1, 60, 62, 63, 65, 66, 67, 68, 70, 72, 74, 75, 76, 77, 78, 79, 80], help = "array of notes for visualizer")

    args = parser.parse_args()

    osc_client = udp_client.SimpleUDPClient(args.ip, args.port)

    # set up encoder
    with open(join(args.json), mode='r') as f:
        #encoder = MelodyEncoder.from_json(f.read())
        encoder_dict = json.load(f)
    encoder = encoder_from_dict(encoder_dict)
    _bars_per_call = encoder_dict['num_bars']
    # create dictionary of notes from encoder
    symbols = [0,1]
    _allowed_pitches = symbols + encoder_dict['allowed_pitches']
    # make a dictionary from encoder. same as encoder.decoder.lut() with added 0 and 1
    _allowed_pitches_dict = dict([i,_allowed_pitches[i]] for i in range(len(_allowed_pitches)))
    print("allowed", _allowed_pitches_dict)

    selected_notes = args.visualizer_notes
    selected_indeces = []

    for k, v in _allowed_pitches_dict.items():
        if v in selected_notes:
            selected_indeces.append(k)
    print("selected", selected_indeces, len(selected_indeces))
    # map note indeces to the visualizer range [0 - 17]
    _visualizer_pitches = dict([i, selected_indeces[i]] for i in range(len(selected_indeces)))
    print("visualizer", _visualizer_pitches)

    print("bars", _bars_per_call)
    # _bars_per_call = 0 ### TODO:
    _seconds_per_bar = 2
    _seconds_per_call = _bars_per_call * _seconds_per_bar

    # dynamic encoder variables
    end_note_time = 0
    time_step = 1 / 8
    call_step_count = 0
    playtimestarts = False
    play_start_time = 0
    is_visualizing = False

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

    # create the osc sending actor
    oscSendActor = OscSendActor()

    barCountActor = BarCountActor(outport=out_port)

    # initiate generation/play actor
    actor = GenPlayActor.start(
    #actor = GenPlayActor(
        outport=out_port, log_midi_files=args.log_midi_files, logdir=logdir,
        crserver_url=args.crserver_url, logger=logger, tempo=args.tempo)
    # atexit.register(actor.stop)

    # enter control loop: reading messages from the input port
    for msg in in_port:

        msg_received = time.time()
        #logger.debug('received message:\n    ' + str(msg) + '\n    at ' + str(msg_received))

        # prune old entries from note_buffer
        n = 0
        while len(note_buffer) > 0 and n < len(note_buffer):
            if msg_received - note_buffer[n].start_time > max_buffer_time:
                logger.debug('removing note From buffer: \n    ' + str(note_buffer[n]))
                del note_buffer[n]
            else:
                n += 1

        if msg.type == 'note_on': #and msg.note is not 61: #TODO:check
            pitch = msg.note
            channel = msg.channel
            velocity = msg.velocity
            note_state = on_notes.pop((channel, pitch), None)
            if note_state is None and velocity != 0:
                # key pressed - add state to on_notes dict
                on_notes[(channel, pitch)] = (velocity, msg_received)

                # send rest note info
                if is_visualizing is True and end_note_time != 0:
                    rest_note_len = msg_received- end_note_time
                    num_rest_steps = math.floor(rest_note_len/time_step)
                    print("rest note", num_rest_steps)
                    if num_rest_steps > 0:
                        for i in range(num_rest_steps):
                            call_step_count += 1
                            osc_client.send_message("/call_index/"+str(call_step_count), 1)

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


                # DYNAMIC ENCODING
                if is_visualizing is True:

                    # turn note into midi
                    inst = pm.Instrument(program=0)
                    note_len = cur_note.end_time - cur_note.start_time
                    visualizer_height = 17

                    pmnote = pm.Note(
                        velocity=cur_note.velocity,
                        pitch=cur_note.pitch,
                        start=0,
                        end=note_len)

                    inst.notes.append(pmnote)
                    midi = pm.PrettyMIDI()
                    midi.instruments.append(inst)
                    num_time_steps = int(math.ceil(note_len / time_step))
                    # print("step", note_len, num_time_steps)

                    # send to encoder
                    note_encoded = encoder.encode(midi)
                    note_encoded = note_encoded[:num_time_steps]
                    # num_time_steps = int(note_len/time_step)+1

                    if (num_time_steps > 64):
                        num_time_steps = 64

                    try:
                        note_encoded.reshape((num_time_steps, 1, encoder.num_symbols)) ####
                    except ValueError as err:
                        # print("ERROR BAD SHAPE ERROR:{0}".format(err))
                        logger.error("ERROR BAD SHAPE ERROR:{0}".format(err))
                        continue

                    live_encoded_note = np.argmax(note_encoded, axis=1)

                    # get returned encoding, send to osc
                    for note in live_encoded_note:
                        call_step_count += 1
                        # remap note inde
                        for k, v in _visualizer_pitches.items():
                            if note == v:
                                osc_client.send_message("/call_index/" + str(call_step_count), int(k)%visualizer_height)

                    # rest note
                    end_note_time = cur_note.end_time
                else:
                    pass
            else:
                logger.error('Key press state error. Dropped a message?')

        # cc's come in on channel 5
        elif msg.channel !=5:
            print("pass on non channel 5 messages")
            pass

        elif msg.type == 'control_change' and msg.control == 19:
            value = msg.value

            if value not in [0, 30]:
                logger.error('Unknown control_change message:\n    ' + str(msg))
                continue
            else:
                if value == 30:
                    is_visualizing = True
                else:
                    is_visualizing = False

        elif msg.type == 'control_change' and msg.control == 20:
            value = msg.value

            if value not in [2, 4, 8, 12]:
                logger.error('Unknown control_change message:\n    ' + str(msg))
                continue
            else:
                response_length_state = value
            most_recent_metronome = msg_received

            # user is changing their input length
            # TODO: Might be bad. Add another reset button in similar way
            if response_length_state != last_response_length_state and model_idle is False:
                logger.info('User changed call length to:     ' + str(response_length_state))
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
                    logger.info('entering ready')

            bars_per_cycle = 2 * value
            call_bars = value

            # increment and report bar count
            bar_count = (bar_count + 1) % bars_per_cycle
            logger.info("bar count: " + str(bar_count))

            barCountActor.tell({'command':'sendbarcount', 'bar_count':bar_count})
            #out_port.send(bar_count_msg)

            # update listening/playing state for max display
            if bar_count == 0:
                #ready_msg = mido.Message(type='control_change', control=15, value=127)
                #out_port.send(ready_msg)
                listening_msg = mido.Message(type='control_change', control=16, value=127)
                out_port.send(listening_msg)

                # clear response visuals
                osc_client.send_message("/response_reset/", 1)
                # FOR VISUALS - reset the step counter to zero at new input
                call_step_count = 0
                print("call_step_count", call_step_count)
                end_note_time = 0
                playtimestarts = False

            if bar_count == 1:
                listening_msg = mido.Message(type='control_change', control=16, value=127)
                out_port.send(listening_msg)
            elif bar_count == call_bars:
                playing_msg = mido.Message(type='control_change', control=17, value=127)
                out_port.send(playing_msg)

            if bar_count >= call_bars and bar_count % _bars_per_call == 0:  # every 2 bars
                print("bars per call", _bars_per_call)
                logger.info('trigger playback at: ' + str(msg_received))
                # send last bar state true on 2, 6, 14 bars otherwise false
                is_last_bar = bar_count == bars_per_cycle - 2
                actor.tell({'command': 'play', 'is_last_bar': is_last_bar})
            # if bar count is in the last bar of response phrase

                # FOR VISUALS to log time of responses playing
                if is_visualizing is True and playtimestarts is False:
                    play_start_time = time.time()
                    playtimestarts = True
                else:
                    pass

        # send midi buffer to trigger model
        elif msg.type == 'control_change' and msg.control == 21 and msg.value == 5:
            trigger_generation = call_bars - 1 <= bar_count < 2*call_bars - 1 and \
                                 bar_count % _bars_per_call == _bars_per_call - 1
            if not trigger_generation:
                continue

            generation_delta = msg_received - most_recent_metronome
            call_start_time = msg_received - (call_bars - 1) * _seconds_per_bar - generation_delta  #early post
            call_end_time = call_start_time + _seconds_per_call
            call_number = (bar_count - _bars_per_call) // 2 + 1

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
                logger.info('entering idle mode'+ str(len(inst.notes)))
                model_idle = True
                bar_count = 0
            else:
                logger.info('call number ' + str(call_number) +' generation triggered '
                            + str(_seconds_per_bar - generation_delta) + ' early')

                midi = pm.PrettyMIDI()
                midi.instruments.append(inst)
                actor.tell({'command': 'generate', 'midi': midi, 'inport':in_port,
                            'responses_dir': args.responses_dir, 'is_visualizing': is_visualizing,
                            'osc_client': osc_client, 'oscSendActor': oscSendActor, 'visualizer_pitches': _visualizer_pitches})

        # send reset notes
        elif msg.type == 'control_change' and msg.control == 23:
            #print("reset notes")
            model_idle = True
            out_port.reset()

        else:
            logger.error('Unknown message type: ' + str(msg))


if __name__ == '__main__':
    main()


'''
/animation/seq, 1
/output_symbols
bundle
call_index
call_index
response_reset

'''
