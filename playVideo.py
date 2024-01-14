import argparse, board, os, random, vlc
from adafruit_apds9960.apds9960 import APDS9960
from gpiozero import Button
from pathlib import Path
from time import sleep

# TODO - prevent screen from turning off? Or will this work even if the screen is off?

# Use command line aargument "-fs" to turn on fullscreen.
print("Starting program...");
basepath = Path(__file__).parent.resolve()
parser = argparse.ArgumentParser()
parser.add_argument('-fs', '--fullscreen', action='store_true')
parser.add_argument('-v', '--videos', action='store', default=os.path.join(basepath, 'videos'))
args = parser.parse_args()

vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()
player.set_fullscreen(args.fullscreen)

def cleanup():
    player.stop()
    player.set_fullscreen(False)
    player.release()
    vlc_instance.release()
    exit()
# Set up button to stop the program if needed.
button = Button(27)
# Use this to stop the program when the button is pressed.
button.when_pressed = cleanup

videos = []
video_files = [
    "TestVideo0.mov",
    "TestVideo1.mov",
    "TestVideo2.mov",
    "TestVideo3.mov",
    "TestVideo4.mov",
    "TestVideo5.mov"]
for video in video_files:
    fullpath = os.path.join(args.videos, video)
    videos.append(vlc_instance.media_new(fullpath))

# refers to videos above, not the default video
canPlayNextVideo = True


# set up default repeating video as playlist so it can repeat
default_video_file = "DefaultVideo.mov"
repeatingMediaList = vlc_instance.media_list_new()
listPlayer = vlc_instance.media_list_player_new()
listPlayer.set_media_list(repeatingMediaList)
listPlayer.set_playback_mode(vlc.PlaybackMode(1)) # looping mode
listPlayer.set_media_player(player)
repeatingMediaList.add_media(os.path.join(args.videos, default_video_file))
repeatingMediaList.lock()
default_video_mrl = repeatingMediaList.item_at_index(0).get_mrl()
repeatingMediaList.unlock()
listPlayer.play()

def playRandomVideo():
    listPlayer.pause()
    # randomly select a video in the list and play it
    randomVideo = random.choice(videos)
    player.set_media(randomVideo)
    player.play()
    duration = player.get_length()
    sleep(duration)


# Set up the sensor
i2c = board.I2C()
apds = APDS9960(i2c)

# Start checking sensor.
apds.enable_proximity = True
# proximity value is from 0 (far) to 255 (close)
proximity_threshold = 50
while True:
    if canPlayNextVideo and apds.proximity > proximity_threshold:
        # Wait and check that it is still this close after half a second.
        sleep(.5)
        if apds.proximity > proximity_threshold:
            # set this immediately so we don't keep going
            canPlayNextVideo = False
            playRandomVideo()
            # don't set play the next video until we are both playing the default video and the proximity sensor is far
            while not canPlayNextVideo:
                defaultVideoIsPlaying = default_video_mrl in player.get_media().get_mrl()
                canPlayNextVideo = (apds.proximity <= 0) and defaultVideoIsPlaying