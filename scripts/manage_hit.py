#!/usr/bin/env python
# encoding: utf-8
import argparse
import cPickle as pickle
from clint.textui import puts, colored
from boto.mturk.connection import MTurkConnection

def get_all_reviewable_hits(mtc):
    page_size = 30
    hits = mtc.get_reviewable_hits(page_size=page_size)
    print "Total results to fetch %s " % hits.TotalNumResults
    print "Request hits page %i" % 1
    total_pages = float(hits.TotalNumResults) / page_size
    int_total = int(total_pages)
    if total_pages-int_total > 0:
        total_pages = int_total + 1
    else:
        total_pages = int_total
    pn = 1
    while pn < total_pages:
        pn = pn + 1
        print "Request hits page %i" % pn
        temp_hits = mtc.get_reviewable_hits(page_size=page_size, page_number=pn)
        hits.extend(temp_hits)
    return hits

def flush_all_hits(mtc):
    page_size = 50
    hits = mtc.search_hits(page_size=page_size)
    print "Total results to fetch %s " % hits.TotalNumResults
    print "Request hits page %i" % 1
    total_pages = float(hits.TotalNumResults) / page_size
    int_total = int(total_pages)
    if total_pages-int_total > 0:
        total_pages = int_total + 1
    else:
        total_pages = int_total
    pn = 1
    while pn < total_pages:
        pn = pn + 1
        print "Request hits page %i" % pn
        temp_hits = mtc.search_hits(page_size=page_size, page_number=pn)
        hits.extend(temp_hits)

    for hit in hits:
        print 'Deleting HIT: ', hit.HITId
        mtc.expire_hit(hit.HITId)
        mtc.disable_hit(hit.HITId)

def approve_and_disable_all_hits(mtc):
    page_size = 50
    hits = mtc.get_reviewable_hits(page_size=page_size)
    print "Total results to fetch %s " % hits.TotalNumResults
    print "Request hits page %i" % 1
    total_pages = float(hits.TotalNumResults) / page_size
    int_total = int(total_pages)
    if total_pages-int_total > 0:
        total_pages = int_total + 1
    else:
        total_pages = int_total
    pn = 1
    while pn < total_pages:
        pn = pn + 1
        print "Request hits page %i" % pn
        temp_hits = mtc.get_reviewable_hits(page_size=page_size, page_number=pn)
        hits.extend(temp_hits)

    for hit in hits:
        print "-------------------------------------------"
        puts(colored.green("Processing HIT # {}:".format(hit.HITId)))
        assignments = mtc.get_assignments(hit.HITId)
        for assignment in assignments:
            print "    Approved assignment!"
            mtc.approve_assignment(assignment.AssignmentId, feedback='Thank you for your time!')
        mtc.disable_hit(hit.HITId)
        puts(colored.red("HIT # {} disabled!".format(hit.HITId)))

def retrieve_HIT_results(mtc):
    hit_items_mapping = dict()
    mturk_crop_db = pickle.load( open('../mturk_crop_db.pkl', 'rb') )
    for idx in xrange(len(mturk_crop_db)):
        if mturk_crop_db[idx]['hit_id'] != 'n/a':
            if not hit_items_mapping.has_key(mturk_crop_db[idx]['hit_id']):
                hit_items_mapping[mturk_crop_db[idx]['hit_id']] = [idx]
            else:
                hit_items_mapping[mturk_crop_db[idx]['hit_id']].append(idx)

    #print hit_items_mapping

    hits = get_all_reviewable_hits(mtc)

    for hit in hits:
        if not hit_items_mapping.has_key(hit.HITId):
            continue

        print "-------------------------------------------"
        puts(colored.green("HITId : {}".format(hit.HITId)))
        assignments = mtc.get_assignments(hit.HITId)
        answers = []
        cnt = 1
        for assignment in assignments:
            puts(colored.yellow('Assignment: {}'.format(cnt)))
            cnt += 1
            try:
                # parse results
                print "\tAnswers of the worker %s:" % assignment.WorkerId
                for question_form_answer in assignment.answers[0]:
                    answers.append(int(question_form_answer.fields[0]))
                #print answers
                #print

                for idx in hit_items_mapping[hit.HITId]:
                    if mturk_crop_db[idx]['answer'] == answers[mturk_crop_db[idx]['question_idx']]:
                        mturk_crop_db[idx]['vote'] += 1
                        print '\tWorker liked the crop of image #%d!' % idx
                    else:
                        print '\tWorker disliked the crop of image #%d!' % idx

                mtc.approve_assignment(assignment.AssignmentId, feedback='Thank you for your time.')

            except Exception as e:
                puts(colored.red("ERROR: {}".format(e)))

        mtc.disable_hit(hit.HITId)

    pickle.dump(mturk_crop_db, open('../mturk_crop_db.pkl', 'wb'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command line interface for managing tasks pushed to MTurk.')
    parser.add_argument("--prod", type=str, choices="yn", default="n",
        help="Are we working on the production server? Default is 'n'.")

    # Options to set AWS credentials
    parser.add_argument("--access", type=str, default="",
        help="Your AWS access key. Will look for boto configuration file if nothing is provided.")

    parser.add_argument("--secret", type=str, default="",
        help="Your AWS secret access key. Will look for boto configuration file if nothing is provided.")

    # Get arguments from user
    args = parser.parse_args()
    access = args.access
    secret = args.secret

    if args.prod == 'n':
        host = 'mechanicalturk.sandbox.amazonaws.com'
    else:
        host = 'mechanicalturk.amazonaws.com'

    # Open MTurk connection
    if access != "" and secret != "":
        mturk = MTurkConnection(host=host, aws_access_key_id=access, aws_secret_access_key=secret)
    else:
        # Account data saved locally in config boto config file
        # http://code.google.com/p/boto/wiki/BotoConfig
        mturk = MTurkConnection(host=host)

    #retrieve_HIT_results(mturk)
    #approve_and_disable_all_hits(mturk)
    flush_all_hits(mturk)
