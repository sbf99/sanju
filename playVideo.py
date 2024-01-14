import argparse, board, os, random, vlc
from adafruit_apds9960.apds9960 import APDS9960
from gpiozero import Button
from pathlib import Path
from time import sleep

# TODO - prevent screen from turning off? Or will this work even if the screen is off?

# Use command line argument "-fs" to turn on fullscreen.
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

# TODO - possibly look into using chapter markers
black_screen_length = 3000 #ms
video_timestamps = [ # in milliseconds
    19000, # dog
    28000, # poe the cat
    40000, # fan
    46000, # purple doll
    55000, # wooden cat
    64000, # horse stuffie
    76000, # monkey
    86000, # end black screen
]

# Note: Just to test that both types work, we have both files.
#fullpath = os.path.join(args.videos, "all_videos.mov")
fullpath = os.path.join(args.videos, "AllVideosTest.mp4")
media = vlc_instance.media_new(fullpath)
player.set_media(media)

# refers to the non-default random video segments
canPlayNextVideo = True

def playRandomVideo():
    # last video segment is a black screen, so don't include it
    video_index = random.randint(0, len(video_timestamps) - 2)
    start_time = video_timestamps[video_index]
    duration = video_timestamps[video_index + 1] - video_timestamps[video_index]
    player.set_time(start_time)
    while player.get_time() < (video_timestamps[video_index + 1] - black_screen_length):
        sleep(0.5)
    # after playing, go back to default video segment at beginning
    player.set_time(0)

# Set up the sensor
i2c = board.I2C()
apds = APDS9960(i2c)

# Start checking sensor.
apds.enable_proximity = True
# proximity value is from 0 (far) to 255 (close)
proximity_threshold = 50
player.set_time(0)
player.play()
while True:
    sleep(0.5)
    if player.get_time() > (video_timestamps[0] - black_screen_length):
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
                        if timestamp < video_timestamps[0]:
                            canPlayNextVideo = True
                            if timestamp > (video_timestamps[0] - black_screen_length):
                                player.set_time(0)