#!/usr/bin/python3

from PIL import Image, ImageDraw, ImageFont
from operator import mod
from functools import reduce
from random import randrange
from math import sqrt
from argparse import ArgumentParser

defaultSize = (4000, 2000)
fnt = ImageFont.truetype('/mnt/c/Windows/Fonts/Arial.ttf', int(min(defaultSize) / 10))
defaultFontColor = 'yellow'
GR = (1 +  sqrt(5)) / 2 # Golden Ratio

def isSameColor(lhs, rhs):
    isSame = lambda i: abs(lhs[i] - rhs[i]) < 10
    return isSame(0) and isSame(1) and isSame(2)

def adjustColorToNotFuzzyEq(lhs, rhs):
    fuzzyEq = lambda lhs, rhs : abs(lhs - rhs) < 10
    diff = sorted([(l - r, i) for (l, r, i) in zip(lhs, rhs, range(3)) if abs(l - r) < 10])
    for d in diff:
        ind = d[1]
        rhs[ind] = (lhs[ind] + 10) % 256 if d[0] < 0 else (lhs[ind] - 10) % 256
    return rhs

def calcColor(triInd):
    rgb = tuple(map(mod, triInd, (255,255,255)))
    invRGB = list(map(lambda clr: 255 - clr, rgb))
    invRGB = tuple(adjustColorToNotFuzzyEq(rgb, invRGB))
    return {'rgb' : rgb, 'inv' : invRGB}

def randomColour(prohibited):
    for i in range(1000):
        cnd = calcColor((randrange(0, 256), randrange(0, 256), randrange(0, 256)))
        if not isSameColor(prohibited['rgb'], cnd['rgb']) and not isSameColor(prohibited['inv'], cnd['rgb']) \
        and not isSameColor(prohibited['rgb'], cnd['inv']) and not isSameColor(prohibited['inv'], cnd['inv']):
            #print ("randomColor", i, cnd)
            return cnd
    return (randrange(0, 256), randrange(0, 256), randrange(0, 256))

def writeText(colour, picSize, draw):
    text = ("Hello World I am Test Picture!",
        "Fill Color: " + str(colour['rgb']),
        "Font Color: " + str(colour['inv']))
    textSizes = [fnt.font.getsize(phrase)[0] for phrase in text]
    textMaxSz = reduce(lambda a, b: (max(a[0], b[0]), max(a[1], b[1])), textSizes)
    textX = (picSize[0] - textMaxSz[0]) / 2
    stepY = int(textMaxSz[1] / 10 + 1.5)
    height = 2 * (textMaxSz[1] + stepY) * len(text) - stepY
    textY = (picSize[1] - height) / 2
    phraseY = textY
    for ind in range(len(text)):
        phraseX = textX + (textMaxSz[0] - textSizes[ind][0]) / 2
        draw.text((phraseX, phraseY), text[ind], font=fnt, fill=defaultFontColor)
        phraseY += textMaxSz[1] + stepY
        draw.text((phraseX, phraseY), text[ind], font=fnt, fill=colour['inv'])
        phraseY += textMaxSz[1] + stepY
    return (int(textX - 0.01 * textMaxSz[0]),
            int(textY - 0.01 * height),
            int(textX + textMaxSz[0] * 1.01 + 0.5),
            int(textY + height * 1.01 + 0.5))

# 0,0 ------ b[0] --------- b[2] ---------- p[0]
#             |              |               |
#      5      |      4       |      5        |
# b[1]----------------------------------------
#             |              |               |
#      4      |              |      4        |
# b[3]----------------------------------------
#             |              |               |
#      5      |      4       |      5        |
# p[1]----------------------------------------
def getBorders(picSize, inBox):
    # Make sure that a random point is present in every quad same amount of
    # "times". In general for corners it is 5 while cross it is 4. Hence cross
    # rects needs to be added twice.
    b = inBox
    p = picSize
    return ((0, 0, b[0], b[1]), (0, 0, b[2], b[1]), (0, 0, p[0], b[1]),
            (0, 0, b[0], b[3]), (0, 0, b[0], p[1]),
            (b[0], 0, b[2], b[1]), (b[0], 0, b[2], b[1]), (b[0], 0, p[0], b[1]),
            (0, b[1], b[0], b[3]), (0, b[1], b[0], b[3]), (0, b[1], b[0], p[1]),
            (b[2], 0, p[0], b[1]), (b[2], 0, p[0], b[3]), (b[2], 0, p[0], p[1]),
            (b[2], b[1], p[0], b[3]), (b[2], b[1], p[0], b[3]), (b[2], b[1], p[0], p[1]),
            (0, b[3], b[0], p[1]), (0, b[3], b[2], p[1]), (0, b[3], p[0], p[1]),
            (b[0], b[3], b[2], p[1]), (b[0], b[3], b[2], p[1]), (b[0], b[3], p[0], p[1]),
            (b[2], b[3], p[0], p[1]))

def genRectCnd(bbox):
    bw = bbox[2] - bbox[0]
    bh = bbox[3] - bbox[1]
    x = randrange(bw - 2)
    y = randrange(bh - 2)
    w = randrange(1, int(bw - (x + 1)))
    minH = int(min(bh - (y + 1), w / GR))
    maxH = int(min(bh - y, w * GR + 0.5))
    h = randrange(minH, maxH)
    return (bbox[0] + x, bbox[1] + y, bbox[0] + x + 1 + w, bbox[1] + y + 1 + h)

def genRect(borderRects):
    bbox = borderRects[randrange(len(borderRects))]
    mw = (bbox[2] - bbox[0]) / 100
    mh = (bbox[3] - bbox[1]) / 100
    isSmall = lambda rect: (rect[2] - rect[0]) < mw or (rect[3] - rect[1]) < mh
    isThin = lambda rect: (rect[2] - rect[0]) / (rect[3] - rect[1]) < GR * 2 \
                       or (rect[3] - rect[1]) / (rect[2] - rect[0]) < GR * 2
    for i in range(1000):
        cnd = genRectCnd(bbox)
        if not isSmall(cnd): # and not isThin(cnd):
            return cnd
    return genRectCnd(bbox)

#    0     w2      2
# 1  +-------------+
#    |             |
# h2 |             |
#    |             |
# 3  +-------------+
def prepTriangle(draw, colour, rect):
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    w2 = rect[0] + randrange(int(width / 2 + 0.5))
    h2 = rect[1] + randrange(int(height / 2 + 0.5))
    switcher = (
        lambda : ((w2, rect[1]), (rect[2], rect[3]), (rect[0], h2)),
        lambda : ((rect[2], h2), (rect[0], rect[3]), (w2, rect[1])),
        lambda : ((w2, rect[3]), (rect[0], rect[1]), (rect[2], h2)),
        lambda : ((rect[0], h2), (rect[2], rect[1]), (w2, rect[3])),
    )
    triXY = switcher[randrange(len(switcher))]()
    #print(triXY)
    return {'area' : 1/3 * width * height, 'draw' : lambda : draw.polygon(triXY, fill=colour['rgb'], outline=colour['inv'])}

def prepEllipse(draw, colour, rect):
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return {'area' : 3/4 * width * height, 'draw' : lambda : draw.ellipse(rect, fill=colour['rgb'], outline=colour['inv'])}

def prepRectangle(draw, colour, rect):
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return {'area' : width * height, 'draw' : lambda : draw.rectangle(rect, fill=colour['rgb'], outline=colour['inv'])}

def drawFigures(colour, picSize, draw, inBox):
    total = randrange(64, 256)
    borderRects = getBorders(picSize, inBox)
    switcher = (prepTriangle, prepEllipse, prepRectangle)
    amount = len(switcher)
    figures = [switcher[randrange(amount)](draw,  randomColour(colour), genRect(borderRects)) for i in range(total)]
    figures.sort(key=lambda f: f['area'], reverse=True)
    for figure in figures:
        figure['draw']()

def createImage(folder, triInd, picSize):
    colour = calcColor(triInd)
    img = Image.new('RGB', picSize, color=colour['rgb'])
    draw = ImageDraw.Draw(img)
    bBox = writeText(colour, picSize, draw)
    drawFigures(colour, picSize, draw, bBox)
    name = folder + '/testpic_%03d_%03d_%03d.jpeg' % colour['rgb']
    img.save(name)
    return name

def main(amount, folder):
    steps = int(amount ** (1. / 3) + 0.5)
    reds = list(range(0, 256, int((256 - 0) / steps + 0.5)))[:steps]
    blues = list(range(1, 256, int((256 - 1) / steps + 0.5)))[:steps]
    greenSteps = int(max(1, amount / steps / steps))
    greens = list(range(2, 256, int((256 - 2) / greenSteps + 0.5)))[:greenSteps]
    count = 0
    for r in reds:
        for b in blues:
            for g in greens:
                name = createImage(folder, (r,g,b), defaultSize)
                count += 1
                print("%d: %s %.3f%%" % (count, name, 100 * count/amount))
    remain = amount - steps * steps * greenSteps
    if remain > 0:
        greens = list(range(0, 256, int((256 - 2) / remain + 0.5)))[:remain]
        for g in greens:
            name = createImage(folder, (128, g, 128), defaultSize)
            count += 1
            print("%d*: %s %.3f%%" % (count, name, 100 * count/amount))

parser = ArgumentParser(description='Generate random images.')
parser.add_argument('--amount', nargs='?', type=int, default=1, help='amount of images to generate')
parser.add_argument('--folder', nargs='?', type=str, default='./', help='destination folder')

if __name__ == "__main__":
    args = parser.parse_args()
    #args = parser.parse_args('--amount 1 --folder ./pictures'.split())
    main(args.amount, args.folder)
