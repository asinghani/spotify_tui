
def formatTime(sec):
    min = int(float(sec) / 60.0)
    sec = int(float(sec) % 60.0)
    min = str(min)
    sec = str(sec)
    if len(min) < 2:
        min = "0" + min

    if len(sec) < 2:
        sec = "0" + sec

    return min + ":" + sec

def mapRange(value, leftMin, leftMax, rightMin, rightMax):
    return rightMin + ((float(value - leftMin) / float(leftMax - leftMin))  * (rightMax - rightMin))

def scrollableString(text, pos, maxLen):
    if len(text) <= maxLen:
        return text

    n = 10
    length = len(text) + n
    text = text + (" " * n) + text

    pos = pos % length
    return text[pos:pos+maxLen]

