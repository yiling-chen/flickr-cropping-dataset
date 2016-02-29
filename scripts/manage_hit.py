#!/usr/bin/env python
# encoding: utf-8
import argparse
import cPickle as pickle
from clint.textui import puts, colored
from boto.mturk.connection import MTurkConnection

def get_all_reviewable_hits(mtc):
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

def retrieve_cropping_results(mtc):
    hit_items_mapping = dict()
    mturk_crop_db = pickle.load( open('../mturk_crop_db.pkl', 'rb') )
    for idx in xrange(len(mturk_crop_db)):
        if mturk_crop_db[idx]['hit_id'] != 'n/a':
            if not hit_items_mapping.has_key(mturk_crop_db[idx]['hit_id']):
                hit_items_mapping[mturk_crop_db[idx]['hit_id']] = [idx]
            else:
                hit_items_mapping[mturk_crop_db[idx]['hit_id']].append(idx)

    hits = get_all_reviewable_hits(mtc)
    log_file = open( '../mturk_crop_log.txt', 'a' )

    for hit in hits:
        if not hit_items_mapping.has_key(hit.HITId):
            continue

        print "-------------------------------------------"
        puts(colored.green("HITId : {}".format(hit.HITId)))
        assignments = mtc.get_assignments(hit.HITId)
        log_file.write('%s\n' % hit.HITId)
        for idx in hit_items_mapping[hit.HITId]:
            log_file.write('%s ' % idx)
        log_file.write('\n')

        for assignment in assignments:
            answers = []
            try:
                # parse results
                #print "\tAnswers of the worker %s:" % assignment.WorkerId
                for question_form_answer in assignment.answers[0]:
                    answers.append(int(question_form_answer.fields[0]))
                #print answers
                log_file.write('%s\n' % assignment.WorkerId)
                for ans in answers:
                   log_file.write('%s ' % ans)
                log_file.write('\n')
                #print

                for idx in hit_items_mapping[hit.HITId]:
                    if mturk_crop_db[idx]['answer'] == answers[mturk_crop_db[idx]['question_idx']]:
                        mturk_crop_db[idx]['vote'] += 1

                mtc.approve_assignment(assignment.AssignmentId, feedback='Thank you for your time!')

            except Exception as e:
                puts(colored.red("ERROR: {}".format(e)))

        for idx in hit_items_mapping[hit.HITId]:
            print 'Photo #', idx, 'received', mturk_crop_db[idx]['vote'], 'votes.'

        mtc.disable_hit(hit.HITId)

    log_file.close()
    pickle.dump(mturk_crop_db, open('../mturk_crop_db.pkl', 'wb'))

def retrieve_ranking_results(mtc):
    hit_items_mapping = dict()
    mturk_rank_db = pickle.load( open('../mturk_rank_db.pkl', 'rb') )
    for idx in xrange(len(mturk_rank_db)):
        if mturk_rank_db[idx]['hit_id'] != 'n/a':
            if not hit_items_mapping.has_key(mturk_rank_db[idx]['hit_id']):
                hit_items_mapping[mturk_rank_db[idx]['hit_id']] = [idx]
            else:
                hit_items_mapping[mturk_rank_db[idx]['hit_id']].append(idx)

    hits = get_all_reviewable_hits(mtc)
    log_file = open( '../mturk_rank_log.txt', 'a' )

    for hit in hits:
        if not hit_items_mapping.has_key(hit.HITId):
            continue

        print "-------------------------------------------"
        puts(colored.green("HITId : {}".format(hit.HITId)))
        assignments = mtc.get_assignments(hit.HITId)
        log_file.write('%s\n' % hit.HITId)
        for idx in hit_items_mapping[hit.HITId]:
            log_file.write('%s ' % idx)
        log_file.write('\n')

        for assignment in assignments:
            answers = []
            try:
                # parse results
                #print "\tAnswers of the worker %s:" % assignment.WorkerId
                for question_form_answer in assignment.answers[0]:
                    answers.append(int(question_form_answer.fields[0]))
                #print answers
                log_file.write('%s\n' % assignment.WorkerId)
                for ans in answers:
                   log_file.write('%s ' % ans)
                log_file.write('\n')
                #print

                for idx in hit_items_mapping[hit.HITId]:
                    if answers[mturk_rank_db[idx]['question_idx']] == 0:
                        mturk_rank_db[idx]['vote_for_0'] += 1
                    elif answers[mturk_rank_db[idx]['question_idx']] == 1:
                        mturk_rank_db[idx]['vote_for_1'] += 1

                mtc.approve_assignment(assignment.AssignmentId, feedback='Thank you for your time!')

            except Exception as e:
                puts(colored.red("ERROR: {}".format(e)))

        for idx in hit_items_mapping[hit.HITId]:
            print 'Photo %d : (crop 0 : %d, crop 1: %d)' % (idx, mturk_rank_db[idx]['vote_for_0'], mturk_rank_db[idx]['vote_for_1'])

        mtc.disable_hit(hit.HITId)

    log_file.close()
    pickle.dump(mturk_rank_db, open('../mturk_rank_db.pkl', 'wb'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command line interface for managing tasks pushed to MTurk.')
    parser.add_argument("--prod", type=str, choices="yn", default="n",
        help="Are we working on the production server? Default is 'n'.")
    parser.add_argument(
        '-t', '--type', type=str, choices='cr', default='r',
        help="Choices of task types [c|r] (cropping/ranking) [default is 'r']."
    )
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

    if args.type == 'c':
        retrieve_cropping_results(mturk)
    elif args.type == 'r':
        retrieve_ranking_results(mturk)

    #approve_and_disable_all_hits(mturk)
    #flush_all_hits(mturk)
