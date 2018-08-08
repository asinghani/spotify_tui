# coding=utf8
import sys
import curses
from curses import wrapper
import time
import locale
from functools import partial
from . import api_applescript as api
from . import icons
from .utils import *
import math

"""
s = screen
y = line #
"""

MAX_WIDTH = 150

def getWidth(s):
    return s.getmaxyx()[1]

def getHeight(s):
    return s.getmaxyx()[0]

def getWindowSize(s):
    width = getWidth(s)
    height = getHeight(s)

    if width < 40 or height < 5:
        raise RuntimeError("Window is too small")

    width = min(MAX_WIDTH, width)

    return height, width


def setupColors():
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

def drawTitle(s, y):
    s.insstr(y, 3, "Spotify", curses.color_pair(1) | curses.A_BOLD)
    return y + 1

trackPos = 0
artistPos = 0
albumPos = 0

def drawTrackInfo(s, y, width, mode, enc, scrollSpeed):
    """
    mode 1 = track, 2 = track + artist, 3 = track + artist + album
    """
    global trackPos, artistPos, albumPos

    panelWidth = width - 15
    textWidth = panelWidth - 2

    # Top line
    s.insch(y, 2, curses.ACS_ULCORNER, curses.A_BOLD)
    [s.insch(y, 3 + i, curses.ACS_HLINE, curses.A_BOLD) for i in range(8)]
    s.insch(y, 11, curses.ACS_TTEE, curses.A_BOLD)
    [s.insch(y, 12 + i, curses.ACS_HLINE, curses.A_BOLD) for i in range(panelWidth)]
    s.insch(y, 12 + panelWidth, curses.ACS_URCORNER, curses.A_BOLD)
    y = y + 1

    # Track
    s.insch(y, 2, curses.ACS_VLINE, curses.A_BOLD)
    s.insstr(y, 3, " Track  ", curses.A_BOLD)
    s.insch(y, 11, curses.ACS_VLINE, curses.A_BOLD)
    s.insstr(y, 13, scrollableString(api.getTrack(), int(trackPos), textWidth))
    s.insch(y, 12 + panelWidth, curses.ACS_VLINE, curses.A_BOLD)
    y = y + 1

    if mode > 1:
        # Middle line
        s.insch(y, 2, curses.ACS_LTEE, curses.A_BOLD)
        [s.insch(y, 3 + i, curses.ACS_HLINE, curses.A_BOLD) for i in range(8)]
        s.insch(y, 11, curses.ACS_PLUS, curses.A_BOLD)
        [s.insch(y, 12 + i, curses.ACS_HLINE, curses.A_BOLD) for i in range(panelWidth)]
        s.insch(y, 12 + panelWidth, curses.ACS_RTEE, curses.A_BOLD)
        y = y + 1

        # Artist
        s.insch(y, 2, curses.ACS_VLINE, curses.A_BOLD)
        s.insstr(y, 3, " Artist ", curses.A_BOLD)
        s.insch(y, 11, curses.ACS_VLINE, curses.A_BOLD)
        s.insstr(y, 13, scrollableString(api.getArtist(), int(trackPos), textWidth))
        s.insch(y, 12 + panelWidth, curses.ACS_VLINE, curses.A_BOLD)
        y = y + 1

    if mode > 2:
        # Middle line
        s.insch(y, 2, curses.ACS_LTEE, curses.A_BOLD)
        [s.insch(y, 3 + i, curses.ACS_HLINE, curses.A_BOLD) for i in range(8)]
        s.insch(y, 11, curses.ACS_PLUS, curses.A_BOLD)
        [s.insch(y, 12 + i, curses.ACS_HLINE, curses.A_BOLD) for i in range(panelWidth)]
        s.insch(y, 12 + panelWidth, curses.ACS_RTEE, curses.A_BOLD)
        y = y + 1

        # Album
        s.insch(y, 2, curses.ACS_VLINE, curses.A_BOLD)
        s.insstr(y, 3, " Album  ", curses.A_BOLD)
        s.insch(y, 11, curses.ACS_VLINE, curses.A_BOLD)
        s.insstr(y, 13, scrollableString(api.getAlbum(), int(trackPos), textWidth))
        s.insch(y, 12 + panelWidth, curses.ACS_VLINE, curses.A_BOLD)
        y = y + 1

    # Bottom line
    s.insch(y, 2, curses.ACS_LLCORNER, curses.A_BOLD)
    [s.insch(y, 3 + i, curses.ACS_HLINE, curses.A_BOLD) for i in range(8)]
    s.insch(y, 11, curses.ACS_BTEE, curses.A_BOLD)
    [s.insch(y, 12 + i, curses.ACS_HLINE, curses.A_BOLD) for i in range(panelWidth)]
    s.insch(y, 12 + panelWidth, curses.ACS_LRCORNER, curses.A_BOLD)
    y = y + 1

    trackPos = trackPos + scrollSpeed

    return y

def drawPlayProgress(s, y, width):
    status = api.getStatus()
    length = api.getLength()
    pos = api.getPosition()

    y = y + 1 # Blank Line

    if status == api.STOPPED:
        s.insstr(y, 2, icons.STOP + "  not playing")
        y = y + 1
        y = y + 1 # Blank Line
        return y

    t = ""
    if status == api.PLAYING:
        t = icons.PLAY + "  playing"
    if status == api.PAUSED:
        t = icons.PAUSE + "  paused"

    s.insstr(y, 0, "")
    s.insstr(y, 2, t)

    timeStr = formatTime(pos) + " of " + formatTime(length)
    s.insstr(y, 18, timeStr)


    y = y + 1

    progressBarWidth = width - 9
    progress = mapRange(pos, 0, length, 0.0, float(progressBarWidth))
    progress = int(round(progress) + 0.01)
    s.insstr(y, 5, "[{}>{}]".format((progress - 1) * "=", (progressBarWidth - progress) * " "))
    y = y + 1

    return y

def drawVolume(s, y, width):
    volume = api.getVolume()

    v = volume if volume > 1 else 0
    t = icons.SPEAKER + "  Volume: " + str(v)
    s.insstr(y, 2, t)
    y = y + 1

    volumeBarWidth = width - 9
    pos = mapRange(volume, 0, 100, 0.0, float(volumeBarWidth))
    pos = int(round(pos) + 0.01)
    s.insstr(y, 5, "[{}0{}]".format((pos - 1) * "=", (volumeBarWidth - pos) * " "))
    y = y + 1

    return y

def drawStatus(s, y, width):
    shuffle = api.getShuffle()
    repeat = api.getRepeat()

    s.insstr(y, 2, "Mode: {}{}{}".format(icons.REPEAT + "   " if repeat else "", icons.SHUFFLE + "  " if shuffle else "", "None" if (not shuffle and not repeat) else ""))


    s.insstr(y, width - 21, " (H) Toggle Help ", curses.A_BOLD)

    y = y + 1

    return y

def drawHelpMenu(s, width, height):
    if height == 5:
        s.insstr(0, 0, "Play:       (Space) | Replay Track: (C)")
        s.insstr(1, 0, "Next Track: (N)     | Prev Track:   (B)")
        s.insstr(2, 0, "Shuffle:    (S)     | Repeat:       (R)")
        s.insstr(3, 0, "Volume Up:  (+)     | Volume Down:  (-)")
        s.insstr(4, 0, "Scroll:     (Z)     | Quit:         (Q)")
    else:
        s.insstr(0, 0, "Command Reference   | Close Help:   (H)", curses.A_UNDERLINE)
        s.insstr(1, 0, "Play:       (Space) | Replay Track: (C)")
        s.insstr(2, 0, "Next Track: (N)     | Prev Track:   (B)")
        s.insstr(3, 0, "Shuffle:    (S)     | Repeat:       (R)")
        s.insstr(4, 0, "Volume Up:  (+)     | Volume Down:  (-)")
        s.insstr(5, 0, "Scroll:     (Z)     | Quit:         (Q)")

def drawUI(enc, s):
    global scroll, helpMenu
    height, width = getWindowSize(s)
    y = 0

    if helpMenu:
        drawHelpMenu(s, width, height)
        return

    if height >= 5:
        y = drawTitle(s, y)

    x = 3
    if height >= 12:
        x = 3
    elif height >= 10:
        x = 2
    elif height >= 8:
        x = 1

    y = drawTrackInfo(s, y, width, x, enc, 0.1 if scroll else 0)

    if height >= 8:
        y = drawPlayProgress(s, y, width)
    if height >= 14:
        y = drawVolume(s, y, width)

    y = drawStatus(s, y, width)

last = -1
scroll = False
helpMenu = False

def runCommands(char):
    global last, scroll, trackPos, helpMenu

    if char == ord("+") or char == ord("="):
        api.volUp()

    if char == ord("-") or char == ord("_"):
        api.volDown()

    elif char == -1 and last != -1:
        if last == ord("p") or last == ord(" "):
            api.playPause()

        if last == ord("n") or last == curses.KEY_RIGHT:
            api.next()

        if last == ord("b") or last == curses.KEY_LEFT:
            api.prev()

        if last == ord("s"):
            api.toggleShuffle()

        if last == ord("r"):
            api.toggleRepeat()

        if last == ord("c"):
            api.restart()

        if last == ord("q"):
            sys.exit(0)

        if last == ord("z"):
            scroll = not scroll
            trackPos = 0

        if last == ord("h"):
            helpMenu = not helpMenu

    last = char

def start(enc, s):
    api.init()

    curses.use_default_colors()
    curses.curs_set(0)

    setupColors()
    s.nodelay(True)
    s.clear()
    s.immedok(False)

    while True:
        char = s.getch()
        curses.flushinp()

        runCommands(char)
        s.erase()
        drawUI(enc, s)

        s.refresh()
        time.sleep(0.01)

def main():
    locale.setlocale(locale.LC_ALL, "")
    enc = locale.getpreferredencoding()
    wrapper(partial(start, enc))

if __name__ == "__main__":
    main()
