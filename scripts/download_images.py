#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import json
import urllib
import argparse
import multiprocessing

if sys.version_info[0] == 3:
    from urllib.request import urlretrieve
else:
    from urllib import urlretrieve

image_folder = '../data/'


def fetch_image(url):
    try:
        filename = os.path.split(url)[-1]
        full_path = os.path.join(image_folder, filename)
        if os.path.exists(full_path):
            return

        print('\tDownloading', filename)
        urlretrieve(url, full_path)
    except urllib.error.HTTPError as e:
        print(e)


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
        print('Creating folder to download images...[{}]'.format(image_folder))
        os.makedirs(image_folder)

    train_json_data = open('../cropping_training_set.json', 'r').read()
    data = json.loads(train_json_data)
    test_json_data = open('../cropping_testing_set.json', 'r').read()
    data.extend(json.loads(test_json_data))
    URLs = [data[i]['url'] for i in range(len(data))]

    print('Downloading {} images with {} workers...'.format(len(data), num_workers))
    pool = multiprocessing.Pool(processes=num_workers)
    pool.map(fetch_image, URLs)
