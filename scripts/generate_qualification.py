#!/usr/bin/env python
# encoding: utf-8
"""
    generate_qualification.py

    Description:
        Functions for generating a qualification test on Mechanical Turk.
        These tests are specific to photo quality assessment tasks designed by the author.
        This is not a general purpose solution!
        The code structure is adopted from:
        https://github.com/drewconway/mturk_coder_quality/blob/master/mturk/boto/generate_qualification.py
        However, the content of the qualification test is substantially rewritten to fit to the new application.
"""
from boto.mturk.price import Price
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion, QuestionContent, Question, QuestionForm
from boto.mturk.question import Overview,AnswerSpecification,SelectionAnswer,FormattedContent
from boto.mturk.qualification import Qualifications, Requirement
import json, urllib, cStringIO
from PIL import Image

class PhotoQualityQualificationTest(object):
    """
        Creates a new Qualification Test object.  The object contains MTurk
        QuestionForm and AnswerForm objects, which are needed to create a new
        qualification test Qualification type.

        Parameters:
        ---------------------
        percent_correct : The minimum  percent of correctly coded sentences
            needed to qualify for this QualificationType

        fp : A file path to a text file with test photo URLs.

        title : Title to be displayed for qualification test

    """
    def __init__(self, fp, percent_correct, title):
        super(PhotoQualityQualificationTest, self).__init__()

        if percent_correct > 1.0 or percent_correct < 0:
            raise ValueError("The value of 'percent_correct' must be in [0,1]")

        # Hold init values
        self.percent_correct = percent_correct
        self.fp = fp
        self.title = title

        # Open data file
        f = open(fp, "r")
        self.__qual_sentences = json.load(f)
        #print self.__qual_sentences
        f.close()

        # Set question data
        self.num_questions = len(self.__qual_sentences)
        #print self.num_questions
        self.min_correct = int(round(self.num_questions * self.percent_correct))

        # Generate sentence data
        self.__qual_test, self.__ans_key = self.__generate_qualification_test(self.__qual_sentences, self.min_correct, self.title)


    def __generate_answer_form(self, sentence_data, question_num):
        '''
            Returns an XML string of the answer key for a given piece of sentence data
        '''
        # Get answer values
        ans = sentence_data['question_'+str(question_num+1)]['Answer']
        #print ans

        # Add policy area answer
        ans_key = "<Question><QuestionIdentifier>photo_pair_"+str(question_num)+"</QuestionIdentifier>"
        ans_key = ans_key + "<AnswerOption><SelectionIdentifier>"+str(ans)+"</SelectionIdentifier>"
        ans_key = ans_key +"<AnswerScore>1</AnswerScore></AnswerOption></Question>"

        return ans_key

    '''
        Generate the XML string that represents a AnswerKey data structure specifying answers for a Qualification test,
        and is used to calculate a score from the key and a Worker's answers.
        See the API reference doc here:
        http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_AnswerKeyDataStructureArticle.html
    '''
    def __generate_answer_key(self, answers, num_correct, num_sentences):

        answer_key = '<?xml version="1.0" encoding="UTF-8"?>'
        answer_key = answer_key + '<AnswerKey xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/AnswerKey.xsd">'
        for a in answers:
            answer_key = answer_key + a

        # Add the qualification value mapping to the answer key
        min_bound = num_correct
        max_bound = num_sentences

        # Add map
        '''
        value_map = "<QualificationValueMapping><RangeMapping><SummedScoreRange>"
        value_map = value_map + "<InclusiveLowerBound>"+str(min_bound)+"</InclusiveLowerBound><InclusiveUpperBound>"+str(max_bound)+"</InclusiveUpperBound>"
        value_map = value_map + "<QualificationValue>1</QualificationValue></SummedScoreRange>"
        value_map = value_map + "<OutOfRangeQualificationValue>5</OutOfRangeQualificationValue>"
        value_map = value_map + "</RangeMapping></QualificationValueMapping>"
        '''
        value_map = "<QualificationValueMapping><PercentageMapping>"
        value_map = value_map + "<MaximumSummedScore>10</MaximumSummedScore>"
        value_map = value_map + "</PercentageMapping></QualificationValueMapping>"

        answer_key = answer_key + value_map +"</AnswerKey>"

        return answer_key

    def __generate_qualification_question(self, sentence_data, question_num):
        '''
            Returns a sentence coding qualification test, with answer key
        '''
        url_left = sentence_data['question_'+str(question_num+1)]['URL_left']
        url_right = sentence_data['question_'+str(question_num+1)]['URL_right']

        # retrieve picture to examine its resolution
        file_left = cStringIO.StringIO(urllib.urlopen(url_left).read())
        img_left = Image.open(file_left)
        left_height = img_left.height
        if left_height > 400:
            left_height = 400

        file_right = cStringIO.StringIO(urllib.urlopen(url_right).read())
        img_right = Image.open(file_right)
        right_height = img_right.height
        if right_height > 400:
            right_height = 400

        options = [('Left', '0'), ('Right','1')]
        question_content = QuestionContent()
        question_content.append_field('Title', 'Indicate which one of the following images is better in terms of composition.')
        question_content.append(FormattedContent('Left:&nbsp;<img src="' + url_left + '" height="' + str(left_height) +
            '" alt="Left picture"></img>Right:&nbsp;<img src="' + url_right + '" height="' + str(right_height) + '" alt="Right picutre"></img>'))
        answer_selection = SelectionAnswer(min=1, max=1, style='radiobutton', selections=options, type='text', other=False)
        question = Question(identifier='photo_pair_'+str(question_num),
                            content=question_content,
                            answer_spec=AnswerSpecification(answer_selection),
                            is_required=True)

        # Glue everything together in a dictionary, keyed by the question_num
        return {"question_num" : question_num,
                "question_"+str(question_num) : question,
                "answer_key_"+str(question_num) : self.__generate_answer_form(sentence_data, question_num)}


    def __generate_qualification_test(self, question_data, num_correct, title):
        '''
            Returns a QuestionForm and AnswerKey for a qualification test from a list of sentence dictionaries.
                question_data : json object containing all the questions.
        '''

        # Get question and answer data
        questions = map(lambda (i,x): self.__generate_qualification_question(x,i), enumerate(question_data))
        answers = map(lambda (i,x): x["answer_key_"+str(i)], enumerate(questions))

        answer_key = self.__generate_answer_key(answers, num_correct, len(question_data))

        # Create form setup
        qual_overview = Overview()
        qual_overview.append_field("Title", title)

        # Instructions
        qual_overview.append(FormattedContent("<h1>Please answer all the questions below.</h1>"))
        qual_overview.append(FormattedContent("<h2>For each question, please choose either the left or right image \
            which you think is more beautiful in terms of its composition. Hints: Please make your decision based on\
            several 'rules of thumb' in photography, such as rule of thirds, visual balance and golden ratio. \
            You may also make your decision by judging which image contains less unimportant or distracting contents.</h2>"))

        # Create question form and append contents
        qual_form = QuestionForm()
        qual_form.append(qual_overview)

        for q in questions:
            i = q["question_num"]
            qual_form.append(q["question_"+str(i)])

        return (qual_form, answer_key)

    def get_question_form(self):
        return self.__qual_test

    def get_answer_form(self):
        return self.__ans_key

    def get_question_sentences(self):
        return self.__qual_sentences

    def get_raw_sentence_data(self):
        return self.__sentences_wt_codings


class PhotoQualityQualificationType(object):
    """
        Register a new QualificationType on MTurk from a test question form and answer key
    """
    def __init__(self, mturk, qualification_test, name, description, keywords, duration, create=False):
        super(PhotoQualityQualificationType, self).__init__()

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

    # Open MTurk connection
    mturk = MTurkConnection(host=host)

    title = "Qualification test for photo quality assessment."

    # Create qualification test object
    qual = PhotoQualityQualificationTest("./qual_question.json", 0.8, title)

    # Qualification Type info
    qual_name = "Qualification Type for Photo Quality Assessment"
    qual_description = "A qualification test in which you are given pairs of photos and asked to pick the more beautiful one."
    qual_keywords = ["photo","quality","ranking"]
    duration = 30 * 60

    # Create new qualification type
    qual_type = PhotoQualityQualificationType(mturk, qual, qual_name, qual_description, qual_keywords, duration, create=True)

