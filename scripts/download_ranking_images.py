#!/usr/bin/env python
import os
import json
import urllib
import argparse
import multiprocessing
from PIL import Image

image_folder = '../data/'

def fetch_image(url):
    filename = os.path.split(url)[-1]
    full_path = os.path.join(image_folder, filename)
    if os.path.exists(full_path):
        return

    print '\tDownloading', filename
    file, mime = urllib.urlretrieve(url)
    photo = Image.open(file)
    photo.save(full_path)

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
    image_folder = args.dir
    num_workers = args.workers

    if num_workers < 0:
        num_workers = multiprocessing.cpu_count() + num_workers

    if not os.path.exists(image_folder):
        print 'Creating folder to download images...[{}]'.format(image_folder)
        os.makedirs(image_folder)

    json_data = open('../ranking_annotation.json', 'r').read()
    data = json.loads(json_data)
    URLs = [data[i]['url'] for i in xrange(len(data))]

    print('Downloading {} images with {} workers...'.format(len(data), num_workers))
    pool = multiprocessing.Pool(processes=num_workers)
    pool.map(fetch_image, URLs)
