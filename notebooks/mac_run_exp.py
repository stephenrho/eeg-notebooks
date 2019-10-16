from muselsl import stream, list_muses, view, record
from multiprocessing import freeze_support, set_start_method, Process, Pool
from mne import Epochs, find_events
from time import time, strftime, gmtime
import os
from utils import utils
from collections import OrderedDict
import sys
from optparse import OptionParser
import warnings
warnings.filterwarnings('ignore')

parser = OptionParser()

parser.add_option("-d", "--duration",
                  dest="duration", type='int', default=400,
                  help="duration of the recording in seconds")
parser.add_option("-s", "--subject",
                  dest="subject", type='int', default=1,
                  help="subject number: must be an integer")
parser.add_option("-r", "--run",
                  dest="run", type='int', default=1,
                  help="run (session) number: must be an integer")
parser.add_option("-e", "--experiment",
                  dest="experiment", type='string', default="n170",
                  help="name of experiment from stimulus_presentation folder")

(options, args) = parser.parse_args()

duration = options.duration
subject = options.subject
session = options.run
experiment = options.experiment
expprez = experiment + '.present'

exec('from stimulus_presentation import ' + experiment)

if experiment == 'visual_p300_stripes':
	recording_path = os.path.join(os.path.expanduser("~"), "eeg-notebooks", "data", "visual", "P300", "subject" + str(subject), "session" + str(session), ("recording_%s.csv" % strftime("%Y-%m-%d-%H.%M.%S", gmtime())))
elif experiment == 'n170':
	recording_path = os.path.join(os.path.expanduser("~"), "eeg-notebooks", "data", "visual", "N170", "subject" + str(subject), "session" + str(session), ("recording_%s.csv" % strftime("%Y-%m-%d-%H.%M.%S", gmtime())))
elif experiment == 'ssvep':
	recording_path = os.path.join(os.path.expanduser("~"), "eeg-notebooks", "data", "visual", "SSVEP", "subject" + str(subject), "session" + str(session), ("recording_%s.csv" % strftime("%Y-%m-%d-%H.%M.%S", gmtime())))
elif experiment == 'nb2020':
	recording_path = os.path.join(os.path.expanduser("~"), "eeg-notebooks", "data", "visual", "nb2020", "subject" + str(subject), "session" + str(session), ("recording_%s.csv" % strftime("%Y-%m-%d-%H.%M.%S", gmtime())))
else:
	print('Experiment name is not correct. Choose from n170, visual_p300_stripes, or ssvep.')

#import pygame
#pygame.init()

stimulus = Process(target=eval(expprez), args=(duration,))
recording = Process(target=record, args=(duration, recording_path))

#stimulus.daemon=True
#recording.daemon=True

if __name__ == '__main__':
    #freeze_support()
    set_start_method('spawn', force=True)
    pool = Pool(processes=4)

    pool.apply_async(eval(expprez), args=(duration,))
    pool.apply_async(record, args=(duration,recording_path))

    pool.close()
    pool.join()
