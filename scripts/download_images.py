#!/usr/bin/env python
import os
import json
import urllib
import argparse
import multiprocessing
from PIL import Image

def fetch_image(url):
    filename = os.path.split(url)[-1]
    if os.path.exists(image_path+filename):
        return

    print '\tDownloading', filename
    file, mime = urllib.urlretrieve(url)
    photo = Image.open(file)
    photo.save(image_path+filename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download the images in the dataset into a specified folder.')
    parser.add_argument(
        '-w', '--workers', type=int, default=-1,
        help="num workers used to download images. -x uses (all - x) cores [-1 default]."
    )
    parser.add_argument('-dir', type=str, default='../data/',
        help='the path to save the images, default="../data/"'
    )
    args = parser.parse_args()
    image_path = args.dir
    num_workers = args.workers

    if num_workers < 0:
        num_workers = multiprocessing.cpu_count() + num_workers

    if not os.path.exists(image_path):
        print 'Creating folder to download images...[{}]'.format(image_path)
        os.makedirs(image_path)

    train_json_data = open('../cropping_training_set.txt', 'r').read()
    data = json.loads(train_json_data)
    test_json_data = open('../cropping_testing_set.txt', 'r').read()
    data.extend(json.loads(test_json_data))
    URLs = [data[i]['url'] for i in xrange(len(data))]

    print('Downloading {} images with {} workers...'.format(len(data), num_workers))
    pool = multiprocessing.Pool(processes=num_workers)
    pool.map(fetch_image, URLs)
