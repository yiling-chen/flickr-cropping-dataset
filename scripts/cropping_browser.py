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
crop_root = '../crops/'
base_url = 'http://cmlab.csie.ntu.edu.tw/~yiling/projects/mturk_cropping/'

def generate_comparison(image, x, y, w, h, filename):
    height, width, channel = image.shape
    scale_o = float(h) / height    # scaling factor of the original image
    new_width = int(width * (float(h) / height))

    total_width = new_width + w + 100
    total_height = h

    crop = image[y:y+h, x:x+w, :]
    canvas = np.ones([total_height, total_width, 3], dtype=np.uint8) * 255
    res = cv2.resize(image, (new_width, h), interpolation=cv2.INTER_CUBIC)

    # randomly shuffle the order of the original and cropped images
    # HIT answer - left : 0, right : 1
    answer = 0
    if randint(0,1) == 1:
        canvas[:res.shape[0], :res.shape[1], :] = res
        canvas[:crop.shape[0], res.shape[1]+100:res.shape[1]+100+crop.shape[1] , :] = crop
        answer = 1
    else:
        canvas[:crop.shape[0], :crop.shape[1], :] = crop
        canvas[:res.shape[0], crop.shape[1]+100:crop.shape[1]+100+res.shape[1], :] = res
        answer = 0

    # Rescaling the composite image to achieve more consistent viewing experience
    if total_width > total_height:
        scale = 1400.0 / total_width
        res = cv2.resize(canvas, (0,0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        cv2.imshow('Comparison', res)
    else:
        scale = 1000.0 / total_height
        res = cv2.resize(canvas, (0,0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        cv2.imshow('Comparison', res)

    # output comparison image
    #cv2.imwrite(filename, res)

    return answer

def browse(database, uname):
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

        #ans = generate_comparison(image=img, x=x, y=y, w=w, h=h, filename=crop_root+filename)

        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)
        cv2.putText(img, username, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2, cv2.CV_AA)
        new_height = int( 640.0/img.shape[1] * img.shape[0])
        res = cv2.resize(img, (640, new_height), interpolation=cv2.INTER_CUBIC)
        cv2.imshow('Cropping', res)
        #cv2.imwrite(crop_root+filename, res)
        key = cv2.waitKey()

        if key == 27:
            print 'exit'
            break

def review(database):
    mturk_crop_db = pickle.load( open('../mturk_crop_db.pkl', 'rb') )
    #mturk_crop_db = []
    stored_photo_id_pool = set()
    for item in mturk_crop_db:
        stored_photo_id_pool.add(item['photo_id'])

    print "Total MTurk DB items: ", len(mturk_crop_db)
    print

    for photo_id, url, username, x, y, w, h in database:
        if photo_id in stored_photo_id_pool:
            continue

        filename = os.path.split(url)[-1]
        path = image_root + filename
        img = cv2.imread(path, cv2.IMREAD_COLOR)

        # Error handling
        if img is None:
            puts(colored.red('ERROR: loading image failed!'))
            continue

        ans = generate_comparison(image=img, x=x, y=y, w=w, h=h, filename=crop_root+filename)

        #cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)
        #cv2.putText(img, username, (10, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2, cv2.CV_AA)
        #new_height = int( 640.0/img.shape[1] * img.shape[0])
        #res = cv2.resize(img, (640, new_height), interpolation=cv2.INTER_CUBIC)
        #cv2.imshow('Cropping', res)
        #cv2.imwrite(crop_root+filename, res)
        key = cv2.waitKey()

        if key == 27:
            print 'exit'
            break
        elif key == 65535:
            print 'delete'
            mturk_crop_db.append(
                { 'photo_id' : photo_id,
                  'hit_id' : 'n/a',
                  'question_idx' : -1,
                  'url' : base_url + filename,
                  'answer' : ans,
                  'num_assignment' : 0,
                  'vote' : 0,
                  'disabled' : True,
                  'valid' : False,
                  'crop' : [x, y, w, h]
                }
            )
        else:
            print 'insert'
            mturk_crop_db.append(
                { 'photo_id' : photo_id,
                  'hit_id' : 'n/a',
                  'question_idx' : -1,
                  'url' : base_url + filename,
                  'answer' : ans,
                  'num_assignment' : 0,
                  'vote' : 0,
                  'disabled' : False,
                  'valid' : False,
                  'crop' : [x, y, w, h]
                }
            )

    #pickle.dump(mturk_crop_db, open('../mturk_crop_db.pkl', 'wb'))

def validate(database):
    mturk_crop_db = pickle.load( open('../mturk_crop_db.pkl', 'rb') )

    for i in xrange(len(mturk_crop_db)):
        if mturk_crop_db[i]['hit_id'] != 'n/a':
            filename = os.path.split(mturk_crop_db[i]['url'])[-1]
            path = image_root + filename
            img = cv2.imread(path, cv2.IMREAD_COLOR)

            # Error handling
            if img is None:
                puts(colored.red('ERROR: loading image failed!'))
                continue

            crop = mturk_crop_db[i]['crop']
            x = crop[0]
            y = crop[1]
            w = crop[2]
            h = crop[3]

            if mturk_crop_db[i]['vote'] > 6:
                cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
            else:
                cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)

            cv2.imshow('Validation', img)
            key = cv2.waitKey()

            if key == 27:
                print 'exit'
                break


def lookup_users():
    username_pool = dict()
    database = pickle.load( open('../cropping_results.pkl', 'rb') )
    for photo_id, url, username, x, y, w, h in database:
        if username not in username_pool.keys():
            username_pool[username] = 1
        else:
            username_pool[username] += 1

    for username in username_pool.keys():
        print username, ':', username_pool[username]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A simple viewer for the photo cropping dataset.')
    parser.add_argument(
        '-u', '--username', type=str, default="Any",
        help="Show the image cropped by the specified user only [default=Any]."
    )
    parser.add_argument(
        '-l', '--list', type=str, choices='yn', default='n',
        help="List all the usernames [default is 'n']."
    )
    parser.add_argument(
        '-m', '--mode', type=str, choices='brv', default='b',
        help="Choices of viewing modes [b|r|v] (browsing/review/validate modes) [default is 'b']."
    )
    args = parser.parse_args()
    uname = args.username

    if args.list == 'y':
        lookup_users()
        sys.exit()

    # load database
    puts(colored.green("Loading database..."))
    db = pickle.load( open('../cropping_results.pkl', 'rb') )
    print "Total cropped images: ", len(db)
    print

    if args.mode == 'r':
        review(database=db)
    elif args.mode == 'b':
        browse(database=db, uname=uname)
    elif args.mode == 'v':
        validate(database=db)

    cv2.destroyAllWindows()
