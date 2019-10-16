"""
task for neurobrite 2020
=============

Face vs. house paradigm stimulus presentation for evoking present.

"""

from time import time, strftime, gmtime
from optparse import OptionParser
from glob import glob
from random import choice
import os

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet


def present(duration=120, subj_num=1, sess_num=1):

    # Create markers stream outlet
    #info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')
    #outlet = StreamOutlet(info)

    markernames = [1, 2, 3, 4]

    # Set up trial parameters
    n_trials = 2010
    iti = 0.8
    soa = 0.5
    jitter = 0.2
    record_duration = np.float32(duration)
    resp_keys = ['z', 'm'] # resp_keys[0] == faces, resp_keys[1] == houses

    # Setup trial list
    image_type = np.random.binomial(1, 0.5, n_trials)
    oddball = np.random.binomial(1, 0.15, n_trials)
    markers = [oddball[i] if image_type[i]==1 else oddball[i]+2 for i in range(n_trials)]

    trials = DataFrame(dict(image_type=image_type,
                            oddball=oddball,
                            mark=markers))#,
                            #timestamp=np.zeros(n_trials)))

    # Setup graphics
    def load_image(filename):
        return visual.ImageStim(win=mywin, image=filename)

    mywin = visual.Window([1600, 900], monitor='testMonitor', units='deg', winType='pygame',
                          fullscr=True)
    text = visual.TextStim(mywin, text="Press %s for faces or %s for buildings. Press either to start..." %(resp_keys[0], resp_keys[1]))

    f1 = list(map(load_image, glob(
        'stim/nb2020/face1/*.jpg')))
    f2 = list(map(load_image, glob(
        'stim/nb2020/face2/*.jpg')))
    b1 = list(map(load_image, glob(
        'stim/nb2020/building1/*.jpg')))
    b2 = list(map(load_image, glob(
        'stim/nb2020/building2/*.jpg')))

    faces = [f1, f2]
    buildings = [b1, b2]

    text.draw()
    mywin.flip()
    event.waitKeys()

    start = time()

    rts = []
    resps = []
    for ii, trial in trials.iterrows():
        # Intertrial interval
        # core.wait(iti + np.random.rand() * jitter)

        # Select and display image
        label = trials['image_type'].iloc[ii]
        odd = trials['oddball'].iloc[ii]

        image = choice(faces[odd] if label == 1 else buildings[odd])
        image.draw()

        # Send marker
        timestamp = time()
        #outlet.push_sample([markernames[trials['mark'].iloc[ii]]], timestamp)
        mywin.flip()

        # offset
        #core.wait(soa)

        # wait for response
        resp_time = soa + iti + np.random.rand() * jitter
        timer = core.CountdownTimer(resp_time)
        response_made = False
        while timer.getTime() > 0:
            if timer.getTime() > resp_time - soa:
                image.draw()
            if not response_made:
                for key in event.getKeys():
                    if key in resp_keys:
                        rts.append(resp_time - timer.getTime())
                        resps.append(key)
                        response_made = True
            mywin.flip()
        if not response_made:
            rts.append("NA")
            resps.append("NA")

        mywin.flip()
        #if len(event.getKeys()) > 0 or (time() - start) > record_duration:
        if "q" in event.getKeys() or (time() - start) > record_duration:
            break
        event.clearEvents()

    #print(resps)
    # write data
    out = trials[0:len(resps)]
    out["rts"] = rts
    out["resps"] = resps
    #print(out)
    file_name = "nb2020-rt" + "_subject" + str(subj_num) + "_session" + str(
        sess_num) + "_" + strftime("%Y-%m-%d-%H.%M.%S", gmtime()) + ".csv"
    file_path = os.path.join(os.path.expanduser("~"), "eeg-notebooks", "data", "visual", "nb2020", "subject" + str(subj_num), "session" + str(sess_num)) + "/"

    if not os.path.exists(file_path):
        os.makedirs(file_path)
    out.to_csv(file_path + file_name)
    # Cleanup
    mywin.close()


def main():
    parser = OptionParser()

    parser.add_option("-d", "--duration",
                      dest="duration", type='int', default=120,
                      help="duration of the recording in seconds.")

    parser.add_option("-s", "--subject",
                      dest="subject", type='int', default=1,
                      help="subject number")

    # one more for version? look for (1) babies, (2) castles, (3) both ?

    (options, args) = parser.parse_args()
    present(options.duration)


if __name__ == '__main__':
    main()
