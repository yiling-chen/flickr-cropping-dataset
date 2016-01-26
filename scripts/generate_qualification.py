#!/usr/bin/env python
# encoding: utf-8
"""
    generate_qualification.py

    Description:
        Functions for generating a qualification test on Mechanical Turk.
        These tests are specific to photo quality assessment tasks designed by the author.
        This is not a general purpose solution!
        This code is partially adopted from:
        https://github.com/drewconway/mturk_coder_quality/blob/master/mturk/boto/generate_qualification.py

    Author: Yi-Ling Chen (yiling.chen.ntu@gmail.com)
"""

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion, QuestionContent, Question, QuestionForm
from boto.mturk.question import Overview,AnswerSpecification,SelectionAnswer,FormattedContent
from boto.mturk.qualification import Qualifications, Requirement

class PhotoQualityQualificationType(object):
    """
        Register a new QualificationType on MTurk from a test question form and and answer key
    """
    def __init__(self, mturk, qualification_test, name, description, keywords, duration, create=False):
        super(CoderQualityQualificationType, self).__init__()

        # Register arguments
        self.mturk = mturk
        self.qualification_test = qualification_test
        self.name = name
        self.description = description
        self.keywords = keywords
        self.duration = duration

        # Placeholder for qualification type
        self.__qual_type = None

        if create:
            self.create()

    def create(self):
        if self.__qual_type is not None:
            raise Warning("This qualification type has already been created!")
            pass
        else:
            self.__qual_type = self.mturk.create_qualification_type(name=self.name,
                                                                description=self.description,
                                                                status="Active",
                                                                retry_delay=60*5,
                                                                keywords=self.keywords,
                                                                test=self.qualification_test.get_question_form(),
                                                                answer_key=self.qualification_test.get_answer_form(),
                                                                test_duration=self.duration)

    def get_type_id(self):
        return self.__qual_type[0].QualificationTypeId

if __name__ == '__main__':
    # Account data saved locally in config boto config file
    # http://code.google.com/p/boto/wiki/BotoConfig
    host = "mechanicalturk.sandbox.amazonaws.com"