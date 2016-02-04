#!/usr/bin/env python
# encoding: utf-8
"""
generate_hit.py

Description:    A command-line interface for generating HITs to MTurk.
                Usage is as follows:
                $ python generate_hit.py -h
                usage: generate_hit.py [-h] [--hits N] [--assign N] [--prod {y,n}]
                       [--access ACCESS] [--secret SECRET]
                This script will push a new experiment to MTurk. Several users defined
                arguments are required.
                optional arguments:
                  -h, --help        show this help message and exit
                  --hits N          The number of HITs to push of this type. Default is 50.
                  --assign N        The number of assignments for each HIT. Default is 30.
                  --prod {y,n}      Should this HIT be pushed to the production server?
                                    Default is 'n'.
                  --access ACCESS   Your AWS access key. Will look for boto configuration file
                                    if nothing is provided
                  --secret SECRET   Your AWS secret access key. Will look for boto
                                    configuration file if nothing is provided

Created by  (yiling.chen.ntu@gmail.com) on
# Copyright (c) , under the Simplified BSD License.
# For more information on FreeBSD see: http://www.opensource.org/licenses/bsd-license.php
# All rights reserved.
"""
from boto.mturk.price import Price
from boto.mturk.connection import MTurkConnection
from boto.mturk.qualification import Qualifications, Requirement
from boto.mturk.question import Question,QuestionForm,QuestionContent,SelectionAnswer,AnswerSpecification,FormattedContent,Overview
from generate_qualification import PhotoQualityQualificationTest,PhotoQualityQualificationType
from clint.textui import puts, colored
from datetime import datetime
import cPickle as pickle
import argparse

def create_hit(mturk, URLs, num_assignment, qualification=Qualifications()):
    # Constant data for HIT generation
    hit_title = "Photo Quality Assessment"
    hit_description = "This task involves viewing pairs of pictures and judging which picture among the image pair is more beautiful."
    #base_reward = 0.05
    lifetime = 259200
    keywords = ["photo","quality","ranking"]
    duration = 30 * 60
    reward = 0.03
    #approval_delay = 86400

    # Question form for the HIT
    question_form = QuestionForm()

    overview = Overview()
    overview.append_field('Title', 'Photo Quality Assessment')
    overview.append(FormattedContent('For each question, please choose either the left or right image which you think is more beautiful in terms of its <u>composition</u>.'))
    overview.append(FormattedContent('<b>Hints: Please make your decision based on several "rules of thumb" in photography, such as rule of thirds, visual balance and golden ratio.</b>'))
    overview.append(FormattedContent('<b>You may also make your decision by judging which image contains less unimportant or distracting contents</b>.'))
    question_form.append(overview)

    ratings = [('Left', '0'), ('Right','1')]
    for i in xrange(len(URLs)):
        qc = QuestionContent()
        qc.append_field('Title', 'Question')
        qc.append_field('Text', 'Please indicate which one of the following images is more beautiful.')
        qc.append(FormattedContent('<img src="'+URLs[i]+'" alt="Image not shown correctly!"></img>'))
        URLs[i]
        fta = SelectionAnswer(min=1, max=1, style='radiobutton', selections=ratings, type='text', other=False)
        q = Question(identifier='photo_pair_'+str(i),
                    content=qc,
                    answer_spec=AnswerSpecification(fta),
                    is_required=True
        )
        question_form.append(q)

    hit_res = mturk.create_hit(title=hit_title,
                                description=hit_description,
                                reward=Price(amount=reward),
                                duration=duration,
                                keywords=keywords,
                                #approval_delay=approval_delay,
                                question=question_form,
                                #lifetime=lifetime,
                                max_assignments=num_assignment,
                                qualifications=qualification)
    # return HIT ID
    return hit_res[0].HITId

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command line interface for generating HITs to MTurk.')
    parser.add_argument('--hits', metavar='N', type=int, default=5, help="The number of HITs to push. Default is 10.")
    parser.add_argument('--assign', metavar='N', type=int, default=1, help="The number of assignments for each HIT. Default is 7.")
    parser.add_argument("--prod", type=str, choices="yn", default="n",
        help="Should this HIT be pushed to the production server? Default is 'n'.")

    # Options to set AWS credentials
    parser.add_argument("--access", type=str, default="",
        help="Your AWS access key. Will look for boto configuration file if nothing is provided.")

    parser.add_argument("--secret", type=str, default="",
        help="Your AWS secret access key. Will look for boto configuration file if nothing is provided.")

    # Get arguments from user
    args = parser.parse_args()

    # Parse user specified arguments
    num_hits = args.hits
    num_assignment = args.assign
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

    hit_results = []

    #------  Create qualification type  -------
    qual_test_title = "Qualification test for photo quality assessment."
    qual_name = "Qualification Type for Photo Quality Assessment"
    qual_description = "A qualification test in which you are given pairs of photos and asked to pick the more beautiful one."
    qual_keywords = ["photo","quality","ranking"]
    duration = 30 * 60

    # Create qualification test object.  Need to check that the qualification hasn't already been generated.
    # If it has, pull it from the set, otherwise generate it.
    current_quals = mturk.search_qualification_types(query="Photo")
    current_qual_names = map(lambda q: q.Name, current_quals)
    if qual_name not in current_qual_names:
        puts(colored.yellow('Creating new qualification type...'))
        qual_test = PhotoQualityQualificationTest("./qual_question.json", 0.9, qual_test_title)

        # Create new qualification type
        qual_type = PhotoQualityQualificationType(mturk, qual_test, qual_name, qual_description, qual_keywords, duration, create=True)
        qual_id = qual_type.get_type_id()
    else:
        puts(colored.green('Using existing qualification type...'))
        requested_qual = current_qual_names.index(qual_name)
        qual_type = current_quals[requested_qual]
        qual_id = qual_type.QualificationTypeId

    # Register test as a requirement for hit
    req = Requirement(qualification_type_id=qual_id,
                      comparator="GreaterThan",
                      integer_value=90)

    # Add qualification test
    qual = Qualifications()
    qual.add(req)

    num_images_per_hit = 2
    mturk_crop_db = pickle.load( open('../mturk_crop_db.pkl', 'rb') )

    indexes = []
    for i in xrange(len(mturk_crop_db)):
        if mturk_crop_db[i]['hit_id'] == 'n/a' and mturk_crop_db[i]['disabled'] == False:
            indexes.append(i)
        if len(indexes) == num_hits * num_images_per_hit:
            break

    #print indexes
    import math
    num_hits = int( math.ceil(len(indexes) / float(num_images_per_hit)) )

    # Create HITs
    for i in xrange(num_hits):
        print 'Pushing HIT #', i, '...'
        image_indexes = indexes[i*num_images_per_hit:(i+1)*num_images_per_hit]
        print image_indexes
        URLs = [mturk_crop_db[j]['url'] for j in image_indexes]
        #print URLs
        HITId = create_hit(mturk, URLs, num_assignment, qual)
        puts(colored.green('\tID: {}'.format(HITId)))

        # save results
        for idx in xrange(len(image_indexes)):
            mturk_crop_db[image_indexes[idx]]['hit_id'] = HITId
            mturk_crop_db[image_indexes[idx]]['question_idx'] = idx

    pickle.dump( mturk_crop_db, open('../mturk_crop_db.pkl', 'wb') )
