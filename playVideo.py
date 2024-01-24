import argparse, board, math, os, random, vlc
from adafruit_apds9960.apds9960 import APDS9960
from gpiozero import Button
from pathlib import Path
from time import sleep

# Use command line argument "-fs" to turn on fullscreen.
print("Starting Sanju Tree program...");
basepath = Path(__file__).parent.resolve()
parser = argparse.ArgumentParser()
parser.add_argument('-fs', '--fullscreen', action='store_true')
parser.add_argument('-v', '--video', action='store', default=os.path.join(basepath, 'Sanju Project - Test 20240121.mp4'))
args = parser.parse_args()

# testing
print("Using video file: " + args.video)


vlc_instance = vlc.Instance()
player = vlc_instance.media_player_new()
player.set_fullscreen(args.fullscreen)
media = vlc_instance.media_new(args.video)
player.set_media(media)

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

# Duration of black screen between all videos.
black_screen_length = 3000 # ms
# Duration of the looping video that we will show, including black screen at the end.
loop_video_duration = 22000 # ms
# Duration of each of the individual videos, including black screen at the end.
video_duration = 22000 # ms

# refers to the non-default random video segments
canPlayNextVideo = True

def playRandomVideo():
    file_duration = player.get_length()
    num_videos = math.ceil((file_duration - loop_video_duration) / video_duration)
    video_index = random.randint(0, num_videos - 1)
    print("file duration is " + str(file_duration))
    print("num_videos is " + str(num_videos))
    print("video_index is " + str(video_index))
    start_time = loop_video_duration + (video_index * video_duration)
    print("Setting start time of next video to: " + str(start_time))
    player.set_time(start_time)
    while player.get_time() < (start_time + video_duration - black_screen_length):
        sleep(0.5)
    # after playing, go back to default video segment at beginning
    print("Setting start time of next video to: 0")
    player.set_time(0)

# Set up the sensor
i2c = board.I2C()
apds = APDS9960(i2c)

# Start checking sensor.
apds.enable_proximity = True
# Proximity value is from 0 (far) to 255 (close).
# When the IR-transmissive material is covering the sensor,
# default value ranges from 1-200ish, but when the card is then
# placed on top of the IR-transmissive plastic, the value is almost
# always the 255 max. So we'll keep the threshold quite close to that.
proximity_threshold = 250
player.set_time(0)
player.play()
while True:
    sleep(0.5)
    if player.get_time() > (loop_video_duration - black_screen_length):
        print("starting loop video")
        player.set_time(0) # loop the video
    if canPlayNextVideo and apds.proximity > proximity_threshold:
        # Wait and check that it is still this close after half a second.
        sleep(0.5)
        if apds.proximity > proximity_threshold:
            # set this immediately so we don't keep going
            canPlayNextVideo = False
            playRandomVideo()
            # don't set play the next video until we are both playing the default video and the proximity sensor is far
            while not canPlayNextVideo:
                if apds.proximity <= proximity_threshold:
                    sleep(0.5) # wait to check it's still gone after half a second.
                    if apds.proximity <= proximity_threshold:
                        # now we know the card is gone.
                        timestamp = player.get_time()
                        if timestamp < loop_video_duration:
                            canPlayNextVideo = True
                            if timestamp > (loop_video_duration - black_screen_length):
                                print("restarting loop video")
                                player.set_time(0)
