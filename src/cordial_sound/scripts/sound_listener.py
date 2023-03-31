#!/usr/bin/env python3

import rospy
import pyaudio
import time
from qt_respeaker_app.srv import *
from cordial_msgs.msg import Sound


FRAMES_PER_BUFFER = rospy.get_param(
    'cordial/sound/frames_per_buffer', default=512,
)


def get_speaker_device_index():
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        device = p.get_device_info_by_index(i)
        if 'bcm2835 Headphones' in device['name']:
            return i


SPEAKER_DEVICE_INDEX = get_speaker_device_index()


def play_sound(data):

    rospy.loginfo("Sound received")
    
    p = pyaudio.PyAudio()

    """
    Occasionally pyaudio fails to open correctly.  Online resources said that this was likely because This is an attempt to fix it by closing down the node
    and restarting the node. 
    """
    try:
        resp = configMic("AGCGAIN", 1)
        stream = p.open(
            format=data.format,
            channels=data.num_channels,
            rate=data.framerate,
            output=True,
            frames_per_buffer=FRAMES_PER_BUFFER,
            output_device_index=SPEAKER_DEVICE_INDEX,
        )
        stream.write(data.data)
        while stream.is_active():
            resp = configMic("AGCGAIN", 100)
            time.sleep(0.5)
            stream.stop_stream()

        stream.close()
        p.terminate()
    except IOError:
        rospy.signal_shutdown("Audio device appears to be busy")

    rospy.loginfo("Sound played!")

if __name__ == '__main__':


    rospy.init_node('sound_listener')
    configMic = rospy.ServiceProxy('/qt_respeaker_app/tuning/set', tuning_set)
    rospy.Subscriber(rospy.get_param('cordial_sound/play_stream_topic'), Sound, play_sound)
    rospy.wait_for_service('qt_respeaker_app/tuning/set')
    resp = configMic("AGCONOFF", 0)
    rospy.spin()

