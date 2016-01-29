#!/usr/bin/env python
# encoding: utf-8
from boto.mturk.price import Price
from boto.mturk.connection import MTurkConnection
from boto.mturk.qualification import Qualifications, Requirement
from boto.mturk.question import Question,QuestionForm,QuestionContent,SelectionAnswer,AnswerSpecification
from generate_qualification import PhotoQualityQualificationTest,PhotoQualityQualificationType
from datetime import datetime
import argparse

HOST = 'mechanicalturk.sandbox.amazonaws.com'
#HOST = 'mechanicalturk.amazonaws.com'

if __name__ == '__main__':

    # Account data saved locally in config boto config file
    # http://code.google.com/p/boto/wiki/BotoConfig
    mturk = MTurkConnection(
                        #aws_access_key_id=ACCESS_ID,
                        #aws_secret_access_key=SECRET_KEY,
                        host=HOST)

    current_quals = mturk.search_qualification_types(query="Photo")
    current_qual_names = map(lambda q: q.Name, current_quals)
    qual_name = "Photo Qualification Test # 2"
    requested_qual = current_qual_names.index(qual_name)
    qual_type = current_quals[requested_qual]
    qual_id = qual_type.QualificationTypeId

    req = Requirement(qualification_type_id=qual_id,
                      comparator="GreaterThan",
                      integer_value=0)

    # Add qualification test
    qual = Qualifications()
    qual.add(req)

    question_form = QuestionForm()
    ratings = [('Valid', '1'), ('Invalid','0')]
    qc9 = QuestionContent()
    qc9.append_field('Title', 'Picture 5:')
    qc9.append_field('Title', 'Indicate the above image is Valid or Invalid.')
    fta9 = SelectionAnswer(min=1, max=1, style='radiobutton',
                selections=ratings,
                type='text',
                other=False)
    q9 = Question(identifier='raw_photo4',
                content=qc9,
                answer_spec=AnswerSpecification(fta9),
                is_required=True)

    question_form.append(q9)


    num_hit_questions = 6
    hit_title = "Code economic political text"
    hit_description = "This task involves reading sentences from political texts and judging whether these sentences deal with a specific policy area."
    base_reward = 0.11
    lifetime = 259200
    keywords = ["text","coding","political"]
    duration = 30*60
    reward = 0.03

    # Create HITs
    for j in xrange(5):
        hit_res = mturk.create_hit(title=hit_title,
                    description=hit_description,
                    reward=reward,
                    duration=duration,
                    keywords=keywords,
                    # approval_delay=approval_delay,
                    question=question_form,
                    #lifetime=lifetime,
                    max_assignments=1,
                    qualifications=qual)
        #hit_results.extend(hit_res)