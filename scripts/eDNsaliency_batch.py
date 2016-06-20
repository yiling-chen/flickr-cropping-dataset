#!/usr/bin/env python
# encoding: utf-8
'''
eDNsaliency_batch.py

Description:    A script for processing a batch of images to generate the corresponding saliency maps
                by using the software release in the following repository:
                https://github.com/coxlab/edn-cvpr2014

                Usage is as follows:
                $ python eDNsaliency_batch.py -h
                Usage: eDNsaliency_batch.py [--opts] <source_path> <output_path>

                Options:
                -h, --help         show this help message and exit
                --descs=DESCPATH   path to SLM model(s) (default: ./slmBestDescrCombi.pkl)
                --svm=SVMPATH      path to SVM file (default: ./svm-slm-cntr)
                --white=WHITEPATH  path to whitening parameters (default: ./whiten-slm-cntr)
                --fixMap=FIXMAP    fixation map / empirical saliency map, if available
                --histeq           histogram equalization with given empirical saliency map
                                   (default: False); requires empirical saliency map
                --auc              compute AUC for given fixation map (default: False);
                                   requires fixation map
                --no-blur          Do not blur the final saliency map (default: False)
                --src-dir=SRCDIR   source directory of images to be batch processed
                                   (e.g., ../images/)
                --dst-dir=DSTDIR   destination directory for storing the computed saliency
                                   maps (e.g., ../eDN/)

    This scirpt is partially adopted from:
    https://github.com/coxlab/edn-cvpr2014/blob/master/eDNsaliency
    by adding a new function for batch processing.
'''
import optparse
import numpy as np
from scipy import misc
from scipy import ndimage
import logging
import pickle
from os import listdir
from os.path import isfile, join
from clint.textui import progress, puts, colored

from liblinearutil import load_model

from eDNSalModel import EDNSaliencyModel
from evaluation import evaluate_sal_map
from imageOps import hist_equalize_maps

'''
    imgPath : source folder of images
    outPath : output folder of saliency maps

    Note: The saliency maps will be named as the same filename of source images.
          If the same filename exists in the output folder, skip to the next image.
'''
def batchProcess(imgPath, outPath, opts):
    # read eDN model(s)
    descFile = open(opts.descPath, 'r')
    desc = pickle.load(descFile)
    descFile.close()

    nFeatures = np.sum([d['desc'][-1][0][1]['initialize']['n_filters']
                    for d in desc if d != None])

    # load SVM model and whitening parameters
    svm = load_model(opts.svmPath)
    f = open(opts.whitePath, 'r')
    whiteParams = np.asarray([map(float, line.split(' ')) for line in f]).T
    f.close()

    # assemble svm model
    svmModel = {}
    svmModel['svm'] = svm
    svmModel['whitenParams'] = whiteParams

    biasToCntr = (svm.get_nr_feature()-nFeatures) == 1

    model = EDNSaliencyModel(desc, svmModel, biasToCntr)

    puts(colored.yellow("Collecting image filenames..."))
    todo_list = [ f for f in listdir(imgPath) if isfile(join(imgPath,f)) ]
    existing_list = [ f for f in listdir(outPath) if isfile(join(outPath,f)) ]
    #image_list.sort()
    puts("Done")

    for f in todo_list:
        if f not in existing_list:
            print '-------------------------------------------------------------'
            print 'processing', f
            print

            try:
                # read image
                img = misc.imread(join(imgPath,f))
                # compute saliency map
                salMap = model.saliency(img, normalize=False)
                # normalize and save the saliency map to disk
                normSalMap = (255.0 / (salMap.max()-salMap.min()) *
                         (salMap-salMap.min())).astype(np.uint8)
                misc.imsave(join(outPath,f), normSalMap)

            except Exception as e:
                puts(colored.red('ERROR: {}'.format(e)))
                puts(colored.yellow('filename: {}'.format(f)))
        else:
            print '-------------------------------------------------------------'
            puts(colored.yellow('Saliency map already exists! ({})'.format(f)))
            print


def eDNsaliency(imgPath, outPath, opts):
    # read image
    img = misc.imread(imgPath)

    # read eDN model(s)
    descFile = open(opts.descPath, 'r')
    desc = pickle.load(descFile)
    descFile.close()

    nFeatures = np.sum([d['desc'][-1][0][1]['initialize']['n_filters']
                    for d in desc if d != None])

    # load SVM model and whitening parameters
    svm = load_model(opts.svmPath)
    f = open(opts.whitePath, 'r')
    whiteParams = np.asarray([map(float, line.split(' ')) for line in f]).T
    f.close()

    # assemble svm model
    svmModel = {}
    svmModel['svm'] = svm
    svmModel['whitenParams'] = whiteParams

    biasToCntr = (svm.get_nr_feature()-nFeatures) == 1

    # compute saliency map
    model = EDNSaliencyModel(desc, svmModel, biasToCntr)
    salMap = model.saliency(img, normalize=False)

    salMap = salMap.astype('f')
    if not opts.noBlur:
        salMap = ndimage.gaussian_filter(salMap, sigma=30)

    # read fixation map / empirical saliency map
    if opts.fixMap:
        fixMap = misc.imread(opts.fixMap)

        # compute AUC
        if opts.auc:
            auc = evaluate_sal_map(salMap, fixMap)
            logging.info("AUC = %f" % auc)

        # for fair visual comparison, perform histogram equalization with
        # empirical saliency map
        if opts.histeq:
            salMap = hist_equalize_maps(fixMap, salMap)

    # normalize and save the saliency map to disk
    normSalMap = (255.0 / (salMap.max()-salMap.min()) *
                 (salMap-salMap.min())).astype(np.uint8)
    misc.imsave(outPath, normSalMap)


def get_optparser():
    usage = "usage: %prog [--opts] <source_path> <output_path>"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("--descs",
        dest="descPath",
        default='slmBestDescrCombi.pkl', # in current directory
        help="path to SLM model(s) (default: ./slmBestDescrCombi.pkl)")
    parser.add_option("--svm",
        dest="svmPath",
        default='svm-slm-cntr', # in current directory
        help="path to SVM file (default: ./svm-slm-cntr)")
    parser.add_option("--white",
        dest="whitePath",
        default='whiten-slm-cntr', # in current directory
        help="path to whitening parameters (default: ./whiten-slm-cntr)")
    parser.add_option("--fixMap",
        dest="fixMap",
        default=None,
        help="fixation map / empirical saliency map, if available")
    parser.add_option("--histeq",
        action="store_true",
        dest="histeq",
        default=False,
        help="histogram equalization with given empirical saliency map "
             "(default: False); requires empirical saliency map")
    parser.add_option("--auc",
        action="store_true",
        dest="auc",
        default=False,
        help="compute AUC for given fixation map (default: False); "
             "requires fixation map")
    parser.add_option("--no-blur",
        action="store_true",
        dest="noBlur",
        default=False,
        help="Do not blur the final saliency map (default: False)")
    parser.add_option("--src-dir",
        dest="srcDir",
        default="~/flickr-cropping-dataset/data/",
        help="source directory of images to be batch processed (e.g., ../images/)")
    parser.add_option("--dst-dir",
        dest="dstDir",
        default="~/flickr-cropping-dataset/eDN/",
        help="destination directory for storing the computed saliency maps (e.g., ../eDN/)")

    return parser

def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = get_optparser()
    opts, args = parser.parse_args()

    batchProcess(opts.srcDir, opts.dstDir, opts)


if __name__ == "__main__":
    main()
