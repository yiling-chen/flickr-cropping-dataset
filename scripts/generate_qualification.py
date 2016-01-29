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
        However, the content of the qualification test is substantially rewritten to fit to our application.

    Author: Yi-Ling Chen (yiling.chen.ntu@gmail.com)
"""
from boto.mturk.price import Price
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion, QuestionContent, Question, QuestionForm
from boto.mturk.question import Overview,AnswerSpecification,SelectionAnswer,FormattedContent
from boto.mturk.qualification import Qualifications, Requirement


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
        #f = open(fp, "r")
        #self.__qual_sentences = json.load(f)
        #f.close()
        self.__qual_sentences = ""

        # Set question data
        self.num_questions = 1 #len(self.__qual_sentences)
        self.min_correct = 1 #int(round(self.num_questions * self.percent_correct))

        # Generate sentence data
        self.__qual_test, self.__ans_key = self.__generate_qualification_test(self.__qual_sentences, self.min_correct, self.title)


    def __generate_answer_form(self, sentence_data, question_num):
        '''
            Returns an XML string of the answer key for a given piece of sentence data
        '''

        # Get answer values
        area_ans = sentence_data["policy_area_gold"]
        econ_ans = sentence_data["econ_scale_gold"]
        soc_ans = sentence_data["soc_scale_gold"]
        if econ_ans == "":
            econ_ans = "NA"
        if soc_ans == "":
            soc_ans = "NA"

        # Add policy area answer
        area_key = "<Question><QuestionIdentifier>policy_area_"+str(question_num)+"</QuestionIdentifier>"
        area_key = area_key + "<AnswerOption><SelectionIdentifier>"+str(area_ans)+"</SelectionIdentifier>"
        area_key = area_key +"<AnswerScore>1</AnswerScore></AnswerOption></Question>"

        econ_key = "<Question><QuestionIdentifier>econ_scale_"+str(question_num)+"</QuestionIdentifier>"
        econ_key = econ_key + "<AnswerOption><SelectionIdentifier>"+str(econ_ans)+"</SelectionIdentifier>"
        econ_key = econ_key + "<AnswerScore>0</AnswerScore></AnswerOption></Question>"

        soc_key = "<Question><QuestionIdentifier>soc_scale_"+str(question_num)+"</QuestionIdentifier>"
        soc_key = soc_key + "<AnswerOption><SelectionIdentifier>"+str(soc_ans)+"</SelectionIdentifier>"
        soc_key = soc_key + "<AnswerScore>0</AnswerScore></AnswerOption></Question>"

        return area_key + econ_key + soc_key

    '''
        Generate the XML string that represents a AnswerKey data structure specifying answers for a Qualification test,
        and is used to calculate a score from the key and a Worker's answers.
        See the API reference doc here:
        http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_AnswerKeyDataStructureArticle.html
    '''
    def __generate_answer_key(self, answers, num_correct, num_sentences):
        '''
        answer_key = '<?xml version="1.0" encoding="UTF-8"?>'
        answer_key = answer_key + '<AnswerKey xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/AnswerKey.xsd">'
        for a in answers:
            answer_key = answer_key + a

        # Add the qualification value mapping to the answer key
        min_bound = num_correct
        max_bound = num_sentences

        # Add map
        value_map = "<QualificationValueMapping><RangeMapping><SummedScoreRange>"
        value_map = value_map + "<InclusiveLowerBound>"+str(min_bound)+"</InclusiveLowerBound><InclusiveUpperBound>"+str(max_bound)+"</InclusiveUpperBound>"
        value_map = value_map + "<QualificationValue>1</QualificationValue></SummedScoreRange>"
        value_map = value_map + "<OutOfRangeQualificationValue>0</OutOfRangeQualificationValue>"
        value_map = value_map + "</RangeMapping></QualificationValueMapping>"

        answer_key = answer_key + value_map +"</AnswerKey>"
        '''

        answer_key = '<?xml version="1.0" encoding="UTF-8"?>'
        answer_key = answer_key + '<AnswerKey xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/AnswerKey.xsd">'

        question_key = "<Question><QuestionIdentifier>raw_photo</QuestionIdentifier>"
        question_key = question_key + "<AnswerOption><SelectionIdentifier>0</SelectionIdentifier>"
        question_key = question_key + "<AnswerScore>100</AnswerScore></AnswerOption></Question>"

        answer_key = answer_key + question_key

        # Add map
        value_map = "<QualificationValueMapping><RangeMapping><SummedScoreRange>"
        value_map = value_map + "<InclusiveLowerBound>0</InclusiveLowerBound><InclusiveUpperBound>100</InclusiveUpperBound>"
        value_map = value_map + "<QualificationValue>50</QualificationValue></SummedScoreRange>"
        value_map = value_map + "<OutOfRangeQualificationValue>0</OutOfRangeQualificationValue>"
        value_map = value_map + "</RangeMapping></QualificationValueMapping>"

        answer_key = answer_key + value_map +"</AnswerKey>"

        return answer_key


    def __generate_qualification_question(self, sentence_data, question_num):
        '''
            Returns a sentence coding qualification test, with answer key
        '''

        # # Coding scale data
        econ_scale = [('', 'NA'),
                      ('Very left','-2'),
                      ('Somewhat left','-1'),
                      ('Neither left nor right','0'),
                      ('Somewhat right','1'),
                      ('Very right','2')]

        soc_scale = [('', 'NA'),
                     ('Very liberal','2'),
                     ('Somewhat liberal','-1'),
                     ('Neither liberal nor conservative','0'),
                     ('Somewhat conservative','1'),
                     ('Very conservative','2')]

        policy_area = [('Select policy area', '0'),
                       ('Not Economic or Social','1'),
                       ('Economic','2'),
                       ('Social','3')]

        # Generate the question text externally.
        tuid = sentence_data["text_unit_id"]
        q_url = "http://s3.amazonaws.com/aws.drewconway.com/mt/experiments/cmp/html/formatted_sentence.html?text_unit_id="
        q_url_formatted = q_url + str(tuid) + "&amp;question_num=" + str(question_num)

        # Create policy area question and answer fields
        content_sentence = QuestionContent()
        content_sentence.append_field("Title", "#" + str(question_num+1))
        content_sentence.append(FormattedContent('<iframe src="'+q_url_formatted+'" frameborder="0" width="1280" height="180" scrolling="auto">This text is necessary to ensure proper XML validation</iframe>'))
        ans_policy_area = SelectionAnswer(min=1, max=1, style="dropdown", selections=policy_area)
        qst_policy_area = Question(identifier = "policy_area_"+str(question_num),
                                  content=content_sentence,
                                  answer_spec=AnswerSpecification(ans_policy_area),
                                  is_required=True)

        # Create 'Economic' policy scale question and answer fields
        content_econ_policy = QuestionContent()
        content_econ_policy.append_field("Text", "If you selected 'Not Economic or Social' the task is complete. Either move to the next sentence, or submit your answers.")
        content_econ_policy.append_field("Text", "If you selected 'Economic', now select economic policy scale below.  Otherwise, do not make a selection.")
        ans_econ_scale = SelectionAnswer(min=1, max=1, style="dropdown", selections=econ_scale)
        qst_econ_policy = Question(identifier = "econ_scale_"+str(question_num),
                                   content = content_econ_policy,
                                   answer_spec = AnswerSpecification(ans_econ_scale),
                                   is_required=True)

        # Create 'Social' policy scale question and answer fields
        content_soc_policy = QuestionContent()
        content_soc_policy.append_field("Text", "If you selected 'Social', now select the social policy scale below.  Otherwise, do not make a selection.")
        ans_soc_scale = SelectionAnswer(min=1, max=1, style="dropdown", selections=soc_scale)
        qst_soc_policy = Question(identifier = "soc_scale_"+str(question_num),
                                  content = content_soc_policy,
                                  answer_spec = AnswerSpecification(ans_soc_scale),
                                  is_required=True)

        # Glue everything together in a dictionary, keyed by the question_num
        return {"question_num" : question_num,
                "policy_area_"+str(question_num) : qst_policy_area,
                "econ_scale_"+str(question_num) : qst_econ_policy,
                "soc_scale_"+str(question_num) : qst_soc_policy,
                "answer_key_"+str(question_num) : self.__generate_answer_form(sentence_data, question_num)}


    def __generate_qualification_test(self, question_data, num_correct, title):
        '''
            Returns a QuestionForm and AnswerKey for a qualification test from a list of sentence dictionaries
        '''

        # Get question and answer data
        #questions = map(lambda (i,x): self.__generate_qualification_question(x,i), enumerate(question_data))
        #answers = map(lambda (i,x): x["answer_key_"+str(i)], enumerate(questions))
        answers = None
        answer_key = self.__generate_answer_key(answers, num_correct, len(question_data))

        # Create form setup
        qual_overview = Overview()
        qual_overview.append_field("Title",title)

        # Instructions
        qual_overview.append(FormattedContent("<h1>You must correctly answer all the questions below.</h1>"))
        qual_overview.append(FormattedContent("<h2>Coding instructions are listed below. Please read through these carefully before continuing on to the coding task.</h2>"))
        inst_url = "https://dl.dropboxusercontent.com/u/43220533/web/criteria.html"
        qual_overview.append(FormattedContent('<iframe src="'+inst_url+'" frameborder="0" width="1280" height="300" scrolling="auto">This text is necessary to ensure proper XML validation</iframe>'))

        # Create question form and append contents
        qual_form = QuestionForm()
        qual_form.append(qual_overview)

        ratings = [('Left', '1'), ('Right','0')]

        qc = QuestionContent()
        qc.append_field('Title', 'Indicate which one of the above images is better in terms of composition.')
        fta1 = SelectionAnswer(min=1, max=1, style='radiobutton',
                        selections=ratings,
                        type='text',
                        other=False)
        q = Question(identifier='raw_photo',
                content=qc,
                answer_spec=AnswerSpecification(fta1),
                is_required=True)

        '''
        for q in questions:
            i = q["question_num"]
            qual_form.append(q["policy_area_"+str(i)])
            qual_form.append(q["econ_scale_"+str(i)])
            qual_form.append(q["soc_scale_"+str(i)])
        '''

        qual_form.append(q)

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
    qual = PhotoQualityQualificationTest("training/", 0.9, title)

    # Qualification Type info
    # qual_name = "Coder Qualification Test "+datetime.now().strftime("%s")
    qual_name = "Photo Qualification Test # 2"
    qual_description = "A qualification test in which you are given pairs of photos and asked to pick the relatively beautiful one."
    qual_keywords = ["photo","quality","ranking"]
    duration = 30*60

    # Create new qualification type
    qual_type = PhotoQualityQualificationType(mturk, qual, qual_name, qual_description, qual_keywords, duration, create=True)

    req = Requirement(qualification_type_id=qual_type.get_type_id(),
                    comparator="GreaterThan",
                    integer_value=0)

    qualification = Qualifications()
    qualification.add(req)

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

    hit = mturk.create_hit(questions = question_form,
                qualifications = qualification,
                max_assignments = 1,
                title = "Test image quality assessment",
                description = "description",
                keywords = "keywords",
                duration = 60*10,
                reward = 0.03)
