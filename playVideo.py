import board, os, random, vlc
from adafruit_apds9960.apds9960 import APDS9960
from gpiozero import Button
from pathlib import Path
from time import sleep

# TODO: Test whether proximity sensor will wake display up from sleep. If not, disable screen blanking on the Pi.
# TODO: Optionally add debug command line argument to turn on and off fullscreen.
print("Starting program...");

vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()
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

# TODO: Turn off fullscreen for debugging. Make this a CLI argument?
player.set_fullscreen(True)
videos = []
video_files = [
    "videos/TestVideo0.mov",
    "videos/TestVideo1.mov",
    "videos/TestVideo2.mov",
    "videos/TestVideo3.mov",
    "videos/TestVideo4.mov",
    "videos/TestVideo5.mov"]
for video in video_files:
    fullpath = os.path.join(os.getcwd(), video)
    videos.append(vlc_instance.media_new(fullpath))

# refers to videos above, not the default video
canPlayNextVideo = True


# MediaList object is required in order to loop the repeating video.
default_video_file = "videos/DefaultVideo.mov"
repeatingMediaList = vlc_instance.media_list_new()
listPlayer = vlc_instance.media_list_player_new()
listPlayer.set_media_list(repeatingMediaList)
listPlayer.set_playback_mode(vlc.PlaybackMode(1)) # looping mode
listPlayer.set_media_player(player)
repeatingMediaList.add_media(os.path.join(os.getcwd(), default_video_file))
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

# TODO: delete these two lines? The interrupts don't seem to work.
# apds.enable_proximity_interrupt = True
# apds.proximity_interrupt_threshold = (0, 175)

# Start checking sensor.
apds.enable_proximity = True
while True:
    # proximity value is from 0 (far) to 255 (close)
    if canPlayNextVideo and apds.proximity > 50:
        # Wait and check that it is still this close after half a second.
        sleep(.5)
        if apds.proximity > 50:
            # set this immediately so we don't keep going
            canPlayNextVideo = False
            playRandomVideo()
            # don't set play the next video until we are both playing the default video and the proximity sensor is far
            while not canPlayNextVideo:
                defaultVideoIsPlaying = default_video_mrl in player.get_media().get_mrl()
                canPlayNextVideo = (apds.proximity < 1) and defaultVideoIsPlaying
                



