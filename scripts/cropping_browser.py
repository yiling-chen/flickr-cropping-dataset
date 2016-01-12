#!/usr/bin/env python
import os
import cv2
from random import randint, shuffle
from clint.textui import puts, colored
try:
    import cPickle as pickle
except:
    import pickle

image_root = '../images/'

if __name__ == '__main__':

    # load database
    puts(colored.green("Loading exsiting database..."))
    database = pickle.load( open('../cropping_results.pkl', 'rb') )
    print "Current records: ", len(database)
    print

    for photo_id, url, username, x, y, w, h in database:
        filename = os.path.split(url)[-1]
        path = image_root + filename
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)
        cv2.putText(img, username, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2, cv2.CV_AA)

        # Error handling
        if img is None:
            puts(colored.red('ERROR: loading image failed!'))
            continue

        cv2.imshow('Cropping', img)
        key = cv2.waitKey(0)

        if key == 27:
            print 'exit'
            break

    cv2.destroyAllWindows()
