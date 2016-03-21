#!/usr/bin/env python
import os
import cv2
import json
import argparse
from random import shuffle

image_root = '../data/'

def browse(database):
    for item in database:
        filename = os.path.split(item['url'])[-1]
        path = image_root + filename
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        crop = item['crop']
        x = crop[0]
        y = crop[1]
        w = crop[2]
        h = crop[3]

        # Error handling
        if img is None:
            puts(colored.red('ERROR: loading image failed!'))
            continue

        cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
        cv2.imshow('Cropping', img)
        key = cv2.waitKey()

        if key == 27:
            print 'exit'
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A simple viewer for the photo cropping dataset.')
    parser.add_argument(
        '-m', '--mode', type=str, choices='cr', default='c',
        help="Choices of viewing modes [c|r] (cropping|ranking) [default is 'c']."
    )
    parser.add_argument(
        '-s', '--shuffle', type=str, choices='yn', default='n',
        help='Randomly shuffle the order of viewing images (yes|no) [default is "n"]'
    )
    args = parser.parse_args()

    print 'Browsing training set...\npress ESC to escape...'
    data = open('../cropping_training_set.txt', 'r').read()
    db = json.loads(data)
    if args.shuffle == 'y':
        shuffle(db)
    browse(db)

    cv2.destroyAllWindows()
