import numpy as np
import cv2
import os, sys, os.path
from matplotlib import pyplot as plt

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    # return the edged image
    return edged

def show(title, img):
    cv2.imshow(title, img)
    cv2.waitKey(0)

def testSize(image, contours):
    height, width = image.shape[:2]
    x1 = min([p[0][0] for p in contours])
    x2 = max([p[0][0] for p in contours])
    tx = x2-x1
    y1 = min([p[0][1] for p in contours])
    y2 = max([p[0][1] for p in contours])
    ty=y2-y1
    #print tx, ty, width * 0.25
    if tx>width * 0.2 or ty>60:
        #print 'plate size is out of range'
        return False
    return True

def testArea(image, contours):
    height, width = image.shape[:2]
    for p in [p[0] for p in contours]:
        tx, ty = p
        _h = int(height * 0.6)
        _w = int(width * 0.8)
        y = int(height * 0.4)
        x = int(width * 0.1)
        isValid = ty>=y and ty<=y + _h and tx>=x and tx<=x + _w
        if not isValid:
            #print 'plate is out of detection area:(tx=%s ty=%s) (x=%s y=%s) (width=%s height=%s)' % (tx, ty, x, y, _w, _h)
            return False
    return True

def testPoints(image, contours):
    #return testArea(image, contours)
    return testSize(image, contours) and testArea(image, contours)

def preProcess(img, isBlur=False):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if isBlur:
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    else:
        blurred = gray
    wide = cv2.Canny(blurred, 10, 200)
    tight = cv2.Canny(blurred, 225, 250)
    auto = auto_canny(blurred)
    canny = wide
    #show('',canny)
    return canny

def getRects(edged):
    ret = []
    #ret, thresh = cv2.threshold(edged, 127, 255, 0)
    (_, cnts, _) = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print '%s rects found' % len(cnts)
    #cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx)>3 and len(approx) < 10: #and cv2.isContourConvex(approx):
            ret.append(approx)
    if not ret:
        print 'no qualified rect found!'
    return ret

def markArea(img, contour, color):
    cv2.drawContours(img, [contour], -1, color, -1)

def mask(file):
    img = cv2.imread(file)
    imgBlur = preProcess(img, True)
    contours = [cont for cont in getRects(imgBlur)]
    #imgCanny = preProcess(img, False)
    #contours.extend([cont for cont in getRects(imgCanny)])
    for _c in contours:
        markArea(img, _c, (0, 255, 0))
    return img

def main(path):
    files = os.listdir(path)
    for file in files:
        pic = os.path.join(path, file)
        if os.path.isfile(pic):
            img = mask(pic)
            show(file, img)

def test():
    file = ".\\cars2\\38.jpg"
    ret = mask(file)
    show(file, ret)

main('.\\cars2\\')
#test()

#cv2.imshow("Edges", np.hstack([tight, auto]))
#cv2.imwrite('ret.jpg', gray)
