import subprocess
import threading
import time
from applescript import AppleScript

STOPPED = 0
PAUSED = 1
PLAYING = 2

track = "N/A"
artist = "N/A"
album = "N/A"
length = 1
pos = 1
status = STOPPED
repeat = False
shuffle = False
volume = 0

commands = {}
prevCommand = AppleScript(source="tell application \"Spotify\"\n set player position to 0\n previous track\n end tell")

def runSpotifyCommand(command):
    try:
        if command not in commands:
            commands[command] = AppleScript(source="tell application \"Spotify\" to "+command)

        return str(commands[command].run()).strip()
    except:
        return "0"

def getTrack():
    return track

def getArtist():
    return artist

def getAlbum():
    return album

def getLength():
    return length

def getPosition():
    return pos


def getStatus():
    return status

def getRepeat():
    return repeat

def getShuffle():
    return shuffle

def getVolume():
    return volume

def update():
    global track, artist, album, length, pos, status, repeat, shuffle, volume
    s = runSpotifyCommand("player state as string")

    if "playing" in s:
        status = PLAYING
    elif "paused" in s:
        status = PAUSED
    else:
        status = STOPPED
        track = "N/A"
        artist = "N/A"
        album = "N/A"
        length = 1
        pos = 1
        repeat = False
        shuffle = False

    if status != STOPPED:
        track = runSpotifyCommand("name of current track as string")
        artist = runSpotifyCommand("artist of current track as string")
        album = runSpotifyCommand("album of current track as string")
        length = int(float(runSpotifyCommand("duration of current track"))) / 1000
        pos = int(float(runSpotifyCommand("player position")))

        repeat = "true" in runSpotifyCommand("repeating").lower()
        shuffle = "true" in runSpotifyCommand("shuffling").lower()

        volume = min(int(runSpotifyCommand("sound volume as integer")) + 1, 100)

def init():
    global thread
    def updateLoop():
        while True:
            update()
            time.sleep(0.3)

    thread = threading.Thread(target=updateLoop)
    thread.daemon = True
    thread.start()

def playPause():
    runSpotifyCommand("playpause")

def volUp():
    global volume
    volume = min(100, volume + 2)
    runSpotifyCommand("set sound volume to " + str(volume))

def volDown():
    global volume
    volume = max(1, volume - 2)
    runSpotifyCommand("set sound volume to " + str(volume))

def next():
    global pos
    pos = 0
    runSpotifyCommand("next track")

def prev():
    global pos
    pos = 0
    prevCommand.run()

def toggleShuffle():
    global shuffle
    shuffle = not shuffle
    runSpotifyCommand("set shuffling to not shuffling")

def toggleRepeat():
    global repeat
    repeat = not repeat
    runSpotifyCommand("set repeating to not repeating")

def restart():
    global pos
    pos = 0
    runSpotifyCommand("set player position to 0")

