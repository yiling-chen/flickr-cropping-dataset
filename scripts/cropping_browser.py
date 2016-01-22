#!/usr/bin/env python
import os
import cv2
import sys
import argparse
import numpy as np
from random import randint, shuffle
from clint.textui import puts, colored
try:
    import cPickle as pickle
except:
    import pickle

image_root = '../images/'

def generate_comparison(image, x, y, w, h):
    height, width, channel = image.shape
    #print height
    #print x, y, w, h
    scale_o = float(h) / height    # scaling factor of the original image
    new_width = int(width * (float(h) / height))

    total_width = new_width + w + 100
    total_height = h

    crop = image[y:y+h, x:x+w, :]
    #print 'crop:', crop.shape
    canvas = np.ones([total_height, total_width, 3], dtype=np.uint8) * 255
    #print 'canvas:', canvas.shape
    res = cv2.resize(img, (new_width, h), interpolation=cv2.INTER_CUBIC)
    #print 'res:', res.shape

    #if randint(0,1) == 1:
    canvas[:res.shape[0], :res.shape[1], :] = res
    canvas[:crop.shape[0], res.shape[1]+100:res.shape[1]+100+crop.shape[1] , :] = crop
    #else:
    #    canvas[:crop.shape[0], :crop.shape[1], :] = crop
    #    canvas[:res.shape[0], crop.shape[1]+100:crop.shape[1]+100+res.shape[1], :] = res

    if total_width > total_height:
        scale = 1400.0 / total_width
        res = cv2.resize(canvas, (0,0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        cv2.imshow('Comparison', res)
    else:
        scale = 1000.0 / total_height
        res = cv2.resize(canvas, (0,0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        cv2.imshow('Comparison', res)

def lookup_users():
    username_pool = set()
    database = pickle.load( open('../cropping_results.pkl', 'rb') )
    for photo_id, url, username, x, y, w, h in database:
        if username not in username_pool:
            username_pool.add(username)

    for username in username_pool:
        print username

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A simple viewer for the photo cropping dataset.')
    parser.add_argument(
        '-u', '--username', type=str, default="Any",
        help="Show the image cropped by the specified user only [default=Any]."
    )
    parser.add_argument(
        '-l', '--list', type=bool, default=False,
        help="List all the usernames [default=False]."
    )
    args = parser.parse_args()
    uname = args.username
    list_users = args.list
    #print uname

    if list_users:
        lookup_users()
        sys.exit()


    # load database
    puts(colored.green("Loading database..."))
    database = pickle.load( open('../cropping_results.pkl', 'rb') )
    print "Current records: ", len(database)
    print

    for photo_id, url, username, x, y, w, h in database:
        if uname != 'Any' and username != uname:
            continue

        filename = os.path.split(url)[-1]
        path = image_root + filename
        img = cv2.imread(path, cv2.IMREAD_COLOR)

        # Error handling
        if img is None:
            puts(colored.red('ERROR: loading image failed!'))
            continue

        generate_comparison(image=img, x=x, y=y, w=w, h=h)

        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)
        cv2.putText(img, username, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2, cv2.CV_AA)
        cv2.imshow('Cropping', img)
        key = cv2.waitKey(0)

        if key == 27:
            print 'exit'
            break

    cv2.destroyAllWindows()
