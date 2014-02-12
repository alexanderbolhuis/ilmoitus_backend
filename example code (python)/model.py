__author__ = 'kvdsluijs & svlemmen'
from abc import abstractmethod
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
import errors
import re
import hashlib
import json
import math
import time
import urllib


#Modelclass Person
class Person(polymodel.PolyModel):
    name = db.StringProperty()
    age = db.IntegerProperty()
    gender = db.StringProperty()
    education_level = db.StringProperty()
    education_type = db.StringProperty()
    profession = db.StringProperty()
    email = db.StringProperty()
    #typeString is not used for recognition, but for displaying the currently logged in user's role (in the welcome
    # screen for example)
    typeString = db.StringProperty()

    # TODO: update view to no longer need anything else than id for short
    def short(self):
        return {'id': self.key().id(),
                'name': self.name,
                'email': self.email}

    def details(self):
        return {'id': self.key().id(),
                'name': self.name,
                'age': self.age,
                'gender': self.gender,
                'educationLevel': self.education_level,
                'educationType': self.education_type,
                'email': self.email,
                'profession': self.profession,
                'typeString': self.typeString}

    def parse(self, data_dict):
        self.name = data_dict['name']
        self.age = int(data_dict['age'])
        self.gender = data_dict['gender']
        self.education_level = data_dict['educationLevel']
        self.education_type = data_dict['educationType']
        self.profession = data_dict['profession']

    def checkDataValidity(self):
        errorList = [self.checkAgeValidity(self.age), self.checkNameValidity(self.name),
                     self.checkGenderValidity(self.gender), self.check_education_level_validity(self.education_level),
                     self.check_education_type_validity(self.education_type)]
        if len(filter(None, errorList)) != 0:
            return errors.InvalidDataError(errorList)

    @abstractmethod
    def setTypeString(self):
        raise NotImplementedError

    def checkNameValidity(self, name):
        if len(name) < 2:
            return errors.InvalidNameError(name)

    def check_education_level_validity(self, education_level):
        valid_values = ["HBO", "WO", "MBO", "Geen"]
        if education_level is None or len(education_level) < 2 or not education_level in valid_values:
            return errors.InvalidEducationLevelError(education_level)

    def check_education_type_validity(self, education_type):
        valid_values = ["Informatica", "Bedrijfskundige informatica", "Wiskunde", "Bedrijfswiskunde en econometrie",
                        "Natuurkunde", "Scheikunde", "Biologie", "Technische bedrijfskunde",
                        "Overige B&#232;ta richtingen",
                        "Alfa richting"]
        if education_type is None or len(education_type) < 2 or not education_type in valid_values:
            return errors.InvalidEducationTypeError(education_type)

    def checkAgeValidity(self, age):
        if age < 0:
            return errors.InvalidAgeError(age)

    def checkGenderValidity(self, gender):
        if gender:
            if gender.islower():
                gender = gender.upper()
                self.gender = gender

            if (self.gender == "M") | (self.gender == "V"):
                return

        return errors.InvalidGenderError(gender)

    def checkEmailValidity(self, email):
        if not re.match(r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*"
                        r"[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", email):
            return errors.InvalidEmailError(email)


#Modelclass Coach
class Coach(Person):
#Note: No constructor for the subclasses! For some reason, this messes with the hierarchy that gets implemented by
# polymodel.
    def parse(self, dict):
        super(Coach, self).parse(dict)
        self.email = dict['email']

    def checkDataValidity(self):
        error = super(Coach, self).checkDataValidity()
        if error is not None:
            errorList = error.error_list

            errorList.append(self.checkEmailValidity(self.email))

            if len(filter(None, errorList)) != 0:
                return errors.InvalidDataError(errorList)

    def setTypeString(self):
        self.typeString = "Coach"


#Modelclass Candidate
class Candidate(Person):
#Note: No constructor for the subclasses! For some reason, this messes with the hierarchy that gets implemented by
# polymodel.
    def parse(self, dict):
        super(Candidate, self).parse(dict)
        self.email = dict['email']

    def checkDataValidity(self):
        error = super(Candidate, self).checkDataValidity()
        if error is not None:
            errorList = error.error_list

            errorList.append(self.checkEmailValidity(self.email))

            if len(filter(None, errorList)) != 0:
                return errors.InvalidDataError(errorList)

    def setTypeString(self):
        self.typeString = "Kandidaat"


#Modelclass Guest
class Guest(Person):
#Note: No constructor for the subclasses! For some reason, this messes with the hierarchy that gets implemented by
# polymodel.
    def setTypeString(self):
        self.typeString = "Gast"


#Modelclass PdfFile
class PdfFile(db.Model):
    pdfFile = db.BlobProperty()
    fileName = db.StringProperty()

    def short(self):
        return {'id': self.key().id()}

    def details(self):
        return {'id': self.key().id(),
                'fileName': self.fileName}

    def parse(self, data_dict):
        self.fileName = data_dict['fileName']


#Modelclass IAnswerFactory
class IAnswerFactory(polymodel.PolyModel):
    @abstractmethod
    def createAnswer(self, description, value):
        raise NotImplementedError


#Modelclass MultipleChoiceAnswerFactory
class MultipleChoiceAnswerFactory(IAnswerFactory):
    def createAnswer(self, description, value):
        self.answer = MultipleChoiceAnswer()
        self.answer.description = description
        self.answer.value = value
        return self.answer

    def setKnowledgeAreas(self, knowledgeAreas):
        for knowledgeArea in knowledgeAreas:
            self.answer.knowledgeAreas.append(knowledgeArea)


#Modelclass OpenQuestionAnswerFactory
class OpenQuestionAnswerFactory(IAnswerFactory):
    def createAnswer(self, description, value):
        self.answer = OpenAnswer()
        self.answer.description = description
        self.answer.value = value
        return self.answer


#Modelclass MBTIAnswerFactory
class MBTIAnswerFactory(IAnswerFactory):
    def createAnswer(self, description, value):
        self.answer = MBTIAnswer()
        self.answer.description = description
        self.answer.value = value
        return self.answer

    def setMBTIType(self, mbtiType):
        self.mbtiType = mbtiType


#Modelclass CalculateScoreStrategy
class CalculateScoreStrategy(polymodel.PolyModel):
    def short(self):
        return {'id': self.key().id_or_name()}

    def details(self):
        return self.short()

    def calculate_final_score(self, all_score_objects):
        invite = None
        date = None
        time_stamp = None
        passed = False
        result = 0.0
        max_result = 0.0
        norm = None
        #version = None todo: version
        data_dict = {}
        for score_object in all_score_objects:
            if invite is None:
                invite = score_object.invite
            if date is None:
                date = score_object.date
            if time_stamp is None:
                time_stamp = score_object.time_taken
            if norm is None and invite is not None:
                norm = invite.exam.norm

            result += float(score_object.earned_value)
            correct_answer_objects = map(lambda correct_key: Answer.get_by_id(correct_key.id_or_name()),
                                         score_object.correct_answers)
            for correct_answer_object in correct_answer_objects:
                #We don't want negative values to influence the max score; skip those
                if correct_answer_object.value > float(0):
                    max_result += float(correct_answer_object.value)
            if not passed and norm is not None:
                passed = (result >= norm)

        data_dict['score_objects'] = map(lambda scoreobject: scoreobject.key(), all_score_objects)
        data_dict['result'] = result
        data_dict['passed'] = passed
        data_dict['date'] = date
        data_dict['time_taken'] = time_stamp
        #data_dict['version'] =
        data_dict['invite'] = invite
        data_dict['max_result'] = max_result
        data_dict['result_percentage'] = round((100 / max_result) * result, 2)
        return data_dict


#Modelclass CalculateMultipleChoiceScore
class CalculateMultipleChoiceScore(CalculateScoreStrategy):
    def generate_score(self, answered_question, date, time_value):
        """
        More a factory method than a strategy; this function creates a single score object for a given answered question.
        It does not do any calculation with this score object yet.
        """
        correct_answer_objects = map(lambda correct_key: Answer.get_by_id(correct_key.id_or_name()),
                                     answered_question.question.correctAnswers)
        invite = answered_question.invite
        earned_knowledge_area_score = {}
        max_knowledge_area_score = {}
        total_earned_value = 0.0

        for correct_answer in correct_answer_objects:
            for knowledge_area in correct_answer.knowledgeAreas:
                #We don't want negative values to influence the max score; skip those
                if correct_answer.value > float(0):
                    earned_knowledge_area_score[knowledge_area] = 0.0
                    if knowledge_area in max_knowledge_area_score.keys():
                        max_knowledge_area_score[knowledge_area] += correct_answer.value
                    else:
                        max_knowledge_area_score[knowledge_area] = correct_answer.value
                    round(max_knowledge_area_score[knowledge_area], 2)

        for given_answer_key in answered_question.givenAnswers:
            given_answer_object = Answer.get_by_id(given_answer_key.id_or_name())
            earned_value = float(given_answer_object.value)
            total_earned_value = float(round(total_earned_value + earned_value, 2))
            for knowledge_area in given_answer_object.knowledgeAreas:
                if knowledge_area in earned_knowledge_area_score.keys():
                    earned_knowledge_area_score[knowledge_area] += earned_value
                else:
                    earned_knowledge_area_score[knowledge_area] = earned_value
                round(earned_knowledge_area_score[knowledge_area], 2)

        multiple_choice_score_object = MultipleChoiceScore()
        multiple_choice_score_object.parse(correct_answer_objects, total_earned_value, earned_knowledge_area_score,
                                           max_knowledge_area_score, invite, date, time_value)
        multiple_choice_score_object.put()
        return multiple_choice_score_object

    def calculate_final_score(self, all_multiple_choice_score_objects):
        base_final_score_dict = super(CalculateMultipleChoiceScore, self).calculate_final_score(
            all_multiple_choice_score_objects)

        all_knowledge_area_dict_earned = {}
        all_knowledge_area_dict_max_values = {}
        knowledge_area_dict_percentages = {}
        total_earned = 0.0
        total_max = 0.0
        try:
            for score_object in all_multiple_choice_score_objects:
                current_earned_dict = json.loads(score_object.knowledge_area_score_earned_json)
                current_max_dict = json.loads(score_object.knowledge_area_score_max_json)

                for key in current_earned_dict.keys():
                    if key in all_knowledge_area_dict_earned.keys():
                        all_knowledge_area_dict_earned[key] += current_earned_dict[key]
                    else:
                        all_knowledge_area_dict_earned[key] = current_earned_dict[key]
                    round(all_knowledge_area_dict_earned[key], 2)
                    total_earned += current_earned_dict[key]
                for key in current_max_dict.keys():
                    #We don't want negative values to influence max score; skip those
                    if current_max_dict[key] > 0:
                        if key in all_knowledge_area_dict_max_values.keys():
                            all_knowledge_area_dict_max_values[key] += current_max_dict[key]
                        else:
                            all_knowledge_area_dict_max_values[key] = current_max_dict[key]
                        round(all_knowledge_area_dict_max_values[key], 2)
                        total_max += current_max_dict[key]

            average_percentage_for_all_knowledge_areas = 0.0
            for key in all_knowledge_area_dict_max_values:
                knowledge_area_dict_percentages[key] = round(((100 / all_knowledge_area_dict_max_values[key]) *
                                                              all_knowledge_area_dict_earned[key]), 2)
                average_percentage_for_all_knowledge_areas += knowledge_area_dict_percentages[key]
            average_percentage_for_all_knowledge_areas = round((average_percentage_for_all_knowledge_areas /
                                                                len(filter(None, all_knowledge_area_dict_max_values))),
                                                               2)
        except Exception as exc:
            print exc.message
            invite_id = all_multiple_choice_score_objects[0].invite.key().id_or_name()
            raise errors.InvalidCalculatingRequest(invite_id)
        total_perc = (100 / total_max) * total_earned
        self_dict = {"knowledge_area_earned_dict": all_knowledge_area_dict_earned,
                     "knowledge_area_max_values_dict": all_knowledge_area_dict_max_values,
                     "knowledge_area_percentages_dict": knowledge_area_dict_percentages,
                     "total_earned_for_all_knowledge_areas": total_earned,
                     "total_max_for_all_knowledge_areas": total_max,
                     "total_percentage_for_all_knowledge_areas": total_perc,
                     "average_percentage_for_all_knowledge_areas": average_percentage_for_all_knowledge_areas}

        complete_data_dict = dict(base_final_score_dict.items() + self_dict.items())
        final_score_object = FinalMultipleChoiceScore()
        final_score_object.parse(complete_data_dict)
        data_error = final_score_object.checkDataValidity()
        if data_error is not None and len(filter(None, data_error.error_list)) > 0:
            for err in filter(None, data_error.error_list):
                print err.msg
            invite_id = all_multiple_choice_score_objects[0].invite.key().id_or_name()
            raise errors.InvalidCalculatingRequest(invite_id)

        return final_score_object


#Modelclass CalculateMBTIScore
class CalculateMBTIScore(CalculateScoreStrategy):
    def generate_score(self, answered_question, date, time):
        for given_answer_key in answered_question.givenAnswers:
            if given_answer_key in answered_question.question.correctAnswers:
                return
                #todo: create mbti score, parse it, put it, return it


#Modelclass CalculateOpenScore
class CalculateOpenScore(CalculateScoreStrategy):
    def generate_score(self, answered_question, date, time):
        for given_answer_key in answered_question.givenAnswers:
            if given_answer_key in answered_question.question.correctAnswers:
                return
                #todo: create mbti score, parse it, put it, return it


#Modelclass Question
class Question(polymodel.PolyModel):
    #Both the original givenAnswer and correctAnswer property have been replaced by an implicitly created property
    # called GivenAnswers and CorrectAnswers respectively.
    description = db.StringProperty(multiline=True)
    imagePath = db.StringProperty()
    maxAnswers = db.IntegerProperty()
    scoreCalculatingStrategy = db.ReferenceProperty(CalculateScoreStrategy)
    answerFactory = db.ReferenceProperty(IAnswerFactory)
    answerOptions = db.ListProperty(db.Key, name="answeroption_set")
    correctAnswers = db.ListProperty(db.Key, name="correctanswer_set")

    def checkDataValidity(self):
        errorList = [self.checkDescriptionValidity(self.description),
                     self.checkMaxAnswersValidity(self.maxAnswers)]
        if len(filter(None, errorList)) != 0:
            return errors.InvalidDataError(errorList)

    def checkDescriptionValidity(self, description):
        if not description:
            return errors.InvalidQuestionDescriptionError(description)

    def setImagePath(self):
        if self.imagePath is None:
            self.imagePath = ""

    def checkMaxAnswersValidity(self, maxAnswers):
        if maxAnswers <= 0:
            return errors.InvalidNumberOfAnswersError(maxAnswers)

    @staticmethod
    def isQuestionValue(question):
        return issubclass(question.__class__, Question)

    def addExistingAnswerOption(self, answer):
        if not self.answerOptionListIsFull():
            answer.put()
            self.answerOptions.append(answer.key())

    def addCorrectAnswer(self, answer):
        if not answer is None and not (answer.key() in self.correctAnswers):
            answer.put()
            self.correctAnswers.append(answer.key())
            self.put()

    def answerOptionListIsFull(self):
        return len(filter(None, self.answerOptions)) >= self.maxAnswers

    @abstractmethod
    def setAnswerFactory(self):
        raise NotImplementedError

    @abstractmethod
    def setScoreCalculatingStrategy(self):
        raise NotImplementedError

    def parse_options_key_collection_to_id_collections(self):
        return map(lambda option: {"id": option.id()}, self.answerOptions)

    def parse_correct_answers_key_collection_to_id_collections(self):
        return map(lambda correct: {"id": correct.id()}, self.correctAnswers)

    def parse_options_id_collection_to_key_collection(self, option_id_list):
        res = map(lambda option: Answer.get_by_id(int(option)).key(), option_id_list)
        return res

    def parse_correct_answers_id_collection_to_key_collection(self, correct_id_list):
        return map(lambda correct: Answer.get_by_id(int(correct)).key(), correct_id_list)

    def short(self):
        return {'id': self.key().id()}

    def details(self):
        return {'id': self.key().id(),
                'description': self.description,
                'answerOptions': self.parse_options_key_collection_to_id_collections(),
                'correctAnswers': self.parse_correct_answers_key_collection_to_id_collections(),
                'scoreCalculatingStrategy': self.scoreCalculatingStrategy.key().id_or_name(),
                'answerFactory': self.answerFactory.key().id_or_name(),
                'imagePath': self.imagePath,
                'maxAnswers': self.maxAnswers}

    def parse(self, data_dict):
        if data_dict is not None and len(filter(None, data_dict)) > 0:
            try:
                self.answerOptions = self.parse_options_id_collection_to_key_collection(data_dict['answerOptions'])
                self.scoreCalculatingStrategy = CalculateScoreStrategy.get_by_id(
                    int(data_dict['scoreCalculatingStrategy']))
                self.description = data_dict["description"]
                self.answerFactory = IAnswerFactory.get_by_id(int(data_dict["answerFactory"]))
                self.correctAnswers = self.parse_correct_answers_id_collection_to_key_collection(
                    data_dict["correctAnswers"])
                self.maxAnswers = data_dict["maxAnswers"]
                if "imagePath" in data_dict and data_dict["imagePath"] is not None and data_dict["imagePath"] != "":
                    self.imagePath = data_dict["imagePath"]
            except KeyError:
                raise errors.InvalidDataForDictionaryError(data_dict)
        else:
            raise errors.InvalidDataForDictionaryError(data_dict)

    def parse_put(self, data_dict):
        if data_dict is not None and len(filter(None, data_dict)) > 0:
            try:
                self.description = data_dict["description"]
                self.imagePath = data_dict["imagePath"]
            except KeyError:
                raise errors.InvalidDataForDictionaryError(data_dict)
        else:
            raise errors.InvalidDataForDictionaryError(data_dict)

    def answerOptionListIsEmpty(self):
        return len(filter(None, self.answerOptions)) <= 0


#Modelclass MultipleChoiceQuestion
class MultipleChoiceQuestion(Question):
    def setAnswerFactory(self):
        answer_factory = MultipleChoiceAnswerFactory.all().get()
        if answer_factory is None:
            answer_factory = MultipleChoiceAnswerFactory()
            answer_factory.put()

        self.answerFactory = answer_factory
        self.put()

    def setScoreCalculatingStrategy(self):
        score_calculating_strategy = CalculateMultipleChoiceScore.all().get()
        if score_calculating_strategy is None:
            score_calculating_strategy = CalculateMultipleChoiceScore()
            score_calculating_strategy.put()

        self.scoreCalculatingStrategy = score_calculating_strategy
        self.put()


#Modelclass OpenQuestion
class OpenQuestion(Question):
    def setAnswerFactory(self):
        answer_factory = OpenQuestionAnswerFactory.all().get()
        if answer_factory is None:
            answer_factory = OpenQuestionAnswerFactory()
            answer_factory.put()

        self.answerFactory = answer_factory
        self.put()

    def setScoreCalculatingStrategy(self):
        score_calculating_strategy = CalculateOpenScore.all().get()
        if score_calculating_strategy is None:
            score_calculating_strategy = CalculateOpenScore()
            score_calculating_strategy.put()

        self.scoreCalculatingStrategy = score_calculating_strategy
        self.put()

    def answerListIsFull(self):
        return True

    def addAnswer(self, answer):
        return None


#Modelclass MBTIQuestion
class MBTIQuestion(Question):
    def setAnswerFactory(self):
        answer_factory = MBTIAnswerFactory.all().get()
        if answer_factory is None:
            answer_factory = MBTIAnswerFactory()
            answer_factory.put()

        self.answerFactory = answer_factory
        self.put()

    def setScoreCalculatingStrategy(self):
        score_calculating_strategy = CalculateMBTIScore.all().get()
        if score_calculating_strategy is None:
            score_calculating_strategy = CalculateMBTIScore()
            score_calculating_strategy.put()

        self.scoreCalculatingStrategy = score_calculating_strategy
        self.put()


#Modelclass Answer
class Answer(polymodel.PolyModel):
    description = db.StringProperty()
    value = db.FloatProperty()

    def checkDataValidity(self):
        errorList = [self.checkDescriptionValidity(self.description)]
        if len(filter(None, errorList)) != 0:
            return errorList
        else:
            return [None]

    def checkDescriptionValidity(self, description):
        if len(description) < 1:
            return errors.InvalidAnswerDescriptionError(description)

    def short(self):
        return {'id': self.key().id()}

    def details(self):
        return {'id': self.key().id(),
                'description': self.description
        }
        # no value; that means that the user can see it in the client side

    def details_admin(self):
        base_dict = self.details()
        base_dict["value"] = self.value  # only admins are allowed to see values
        return base_dict

    def parse(self, data_dict):
        if data_dict is not None and len(filter(None, data_dict)) > 0:
            try:
                self.description = data_dict['description']
                self.value = float(data_dict["value"])
            except (KeyError, ValueError):
                raise errors.InvalidDataForDictionaryError(data_dict)
        else:
            raise errors.InvalidDataForDictionaryError(data_dict)

    def get_extra_answer_data(self):
        return None


#Modelclass MultipleChoiceAnswer
class MultipleChoiceAnswer(Answer):
    knowledgeAreas = db.StringListProperty()

    def checkDataValidity(self):
        superErrorList = super(MultipleChoiceAnswer, self).checkDataValidity()
        selfErrorList = [self.checkKnowledgeAreasValidity(self.knowledgeAreas)]
        completeErrorList = superErrorList + selfErrorList
        if len(filter(None, completeErrorList)) != 0:
            return errors.InvalidDataError(completeErrorList)

    def checkKnowledgeAreasValidity(self, knowledgeAreas):
        errorList = []
        for knowledgeArea in knowledgeAreas:
            if len(knowledgeArea) < 1:
                errorList.append(knowledgeArea)

        if len(errorList) > 0:
            return errors.InvalidKnowledgeAreasError(errorList)

    def details(self):
        superDict = super(MultipleChoiceAnswer, self).details()
        selfDict = {'knowledge_areas': self.knowledgeAreas}
        completeDict = dict(superDict.items() + selfDict.items())
        return completeDict

    def parse(self, data_dict):
        if data_dict is not None and len(filter(None, data_dict)) > 0:
            try:
                super(MultipleChoiceAnswer, self).parse(data_dict)
                if "knowledge_areas" in data_dict.keys():
                    knowledge_area_list = data_dict["knowledge_areas"]
                    if knowledge_area_list is not None and len(filter(None, knowledge_area_list)) > 0:
                        self.knowledgeAreas = knowledge_area_list
                else:
                    self.knowledgeAreas = []
            except KeyError:
                raise errors.InvalidDataForDictionaryError(data_dict)
        else:
            raise errors.InvalidDataForDictionaryError(data_dict)

    def get_extra_answer_data(self):
        return self.knowledgeAreas


#Modelclass OpenAnswer
class OpenAnswer(Answer):
    def checkDataValidity(self):
        errorList = super(OpenAnswer, self).checkDataValidity()
        if len(filter(None, errorList)):
            return errors.InvalidDataError(errorList)
        else:
            return None

    def get_extra_answer_data(self):
        return None


#Modelclass MBTIAnswer
class MBTIAnswer(Answer):
    mbtiType = db.StringProperty()

    def checkDataValidity(self):
        superErrorList = super(MBTIAnswer, self).checkDataValidity()
        selfErrorList = [self.checkMBTITypeValidity(self.mbtiType)]
        completeErrorList = superErrorList + selfErrorList
        if len(filter(None, completeErrorList)) != 0:
            return errors.InvalidDataError(completeErrorList)

    def checkMBTITypeValidity(self, mbtiType):
        if mbtiType is not None:
            if not re.match(r'[EFIJNPST]', mbtiType):
                return errors.InvalidMBTITypeError(mbtiType)
        else:
            return errors.NoMBTITypeError(self)

    def details(self):
        superDict = super(MBTIAnswer, self).details()
        selfDict = {'mbtiType': self.mbtiType}
        completeDict = dict(superDict.items() + selfDict.items())
        return completeDict

    def get_extra_answer_data(self):
        return [self.mbtiType]


#Modelclass QuestionNode
class QuestionNode(db.Model):
    questionValue = db.ReferenceProperty(Question)
    previousNode = db.SelfReferenceProperty(collection_name="previousNodes")
    nextNode = db.SelfReferenceProperty(collection_name="nextNodes")

    def short(self):
        return {'id': self.key().id()}

    def details(self):
        if self.previousNode is None:
            previousValue = None
        else:
            previousValue = self.previousNode.key().id()
        if self.nextNode is None:
            nextValue = None
        else:
            nextValue = self.nextNode.key().id()
        return {'id': self.key().id(),
                'questionValue': self.questionValue.key().id(),
                'previousNode': previousValue,
                'nextNode': nextValue}

    def setQuestionValue(self, question):
        if isinstance(question, Question):
            self.questionValue = question


#Modelclass QuestionDoublyLinkedList
class QuestionDoublyLinkedList(db.Model):
    first = db.ReferenceProperty(QuestionNode, collection_name="firstNode")
    last = db.ReferenceProperty(QuestionNode, collection_name="lastNode")
    currentLink = db.ReferenceProperty(QuestionNode)
    length = db.IntegerProperty(default=0)

    def short(self):
        return {'id': self.key().id_or_name()}

    def details(self):
        return {'id': self.key().id_or_name(),
                'first': self.first.key().id_or_name(),
                'current': self.currentLink.key().id_or_name(),
                'last': self.last.key().id_or_name(),
                'length': self.length}

    def getCurrent(self):
        if self.currentLink is None:
            if self.isEmpty():
                return None

            self.currentLink = self.first

        return self.currentLink

    def insertFirst(self, question):
        questionNode = self.transformToNode(question)
        questionNode.put()
        if self.isEmpty():
            self.last = questionNode
            self.currentLink = self.last
        else:
            self.first.previousNode = questionNode
        questionNode.nextNode = self.first
        self.first = questionNode
        self.first.put()
        if self.first.nextNode is not None:
            self.first.nextNode.put()

        self.length += 1

    def insertLast(self, question):
        questionNode = self.transformToNode(question)
        questionNode.put()
        if self.isEmpty():
            self.first = questionNode
            self.currentLink = self.first
        else:
            self.last.nextNode = questionNode
        questionNode.previousNode = self.last
        self.last = questionNode
        self.last.put()
        if self.last.previousNode is not None:
            self.last.previousNode.put()

        self.length += 1

    def getNodeAt(self, position):
        counter = 0
        current = self.first
        while (current is not None) & (counter <= position):
            if counter == position:
                return current
            current = current.nextNode
            counter += 1
        return None

    def setCurrentNodeAt(self, position):
        self.currentLink = self.getNodeAt(position)

    def deleteQuestion(self, question):
        if self.isEmpty() | (not Question.isQuestionValue(question)):
            return None

        current = self.first
        previous = self.first

        while current.questionValue.key() != question.key():
            if current.nextNode is None:
                return None
            else:
                previous = current
                current = current.nextNode

        if current.key() == self.first.key():
            self.first = current.nextNode
            self.first.previousNode = None
            self.first.put()
        elif current.key() == self.last.key():
            self.last = current.previousNode
            self.last.nextNode = None
            self.last.put()
        else:
            previous.nextNode = current.nextNode
            previous.put()
            current.nextNode.previousNode = current.previousNode
            current.nextNode.put()

        if self.currentLink is None:
            self.currentLink = self.first
            self.currentLink.put()
            self.length -= 1
            return current

        if self.currentLink.questionValue.key() == question.key() and not self.isEmpty():
            self.currentLink = self.first
            self.currentLink.put()
        self.length -= 1
        return current

    def isEmpty(self):
        result = (self.first is None)
        return result

    def transformToNode(self, question):
        if isinstance(question, QuestionNode):
            questionNode = question
        elif Question.isQuestionValue(question):
            questionNode = QuestionNode()
            questionNode.setQuestionValue(question)
        else:
            return
        return questionNode

    def getNext(self):
        return self.currentLink.nextNode

    def getPrevious(self):
        return self.currentLink.previousNode

    def goToNext(self):
        if self.currentLink != self.last:
            self.currentLink = self.currentLink.nextNode
        else:
            return None

    def goToPrevious(self):
        if self.currentLink != self.first:
            self.currentLink = self.currentLink.previousNode
        else:
            return None


#Modelclass Exam
class Exam(db.Model):
    title = db.StringProperty()
    norm = db.IntegerProperty()
    timer = db.IntegerProperty()
    questions = db.ReferenceProperty(QuestionDoublyLinkedList)

    def short(self):
        return {'id': self.key().name()}

    def details(self):
        return {'id': self.key().name(),
                'title': self.title,
                'norm': self.norm,
                'timer': self.timer,
                'questions': self.questions.key().id_or_name()
        }

    def parse(self, data_dict):
        self.title = data_dict['title']
        self.norm = int(data_dict['norm'])
        self.timer = int(data_dict['timer'])
        self._key_name = self.title

    def add_question_to_exams_linked_list(self, question):
        self.questions.insertLast(question)
        question.put()
        self.questions.put()
        return question

    def check_title_validity(self, title):
        if title is not None:
            try:
                safe_title = str(title)
                if safe_title is not "":
                    return
            except ValueError:
                return errors.InvalidExamTitleError(title)
        return errors.InvalidExamTitleError(title)

    def check_norm_validity(self, norm):
        if norm is not None:
            try:
                safe_norm = int(norm)
                if safe_norm >= 0:
                    return
            except ValueError:
                return errors.InvalidExamNormError(norm)
        return errors.InvalidExamNormError(norm)

    def check_timer_validity(self, timer):
        if timer is not None:
            try:
                safe_norm = int(timer)
                if safe_norm >= 0:
                    return
            except ValueError:
                return errors.InvalidExamTimerError(timer)
        return errors.InvalidExamTimerError(timer)

    def check_questions_reference_validity(self, questions):
        if questions is not None:
            if questions.key().has_id_or_name():
                return
        return errors.InvalidExamQuestionsReferenceError(questions)

    def check_data_validity(self):
        error_list = [self.check_title_validity(self.title),
                      self.check_norm_validity(self.norm),
                      self.check_timer_validity(self.timer),
                      self.check_questions_reference_validity(self.questions)]
        print error_list
        if len(filter(None, error_list)) > 0:
            return errors.InvalidDataError(error_list)


#Modelclass Invite
class Invite(polymodel.PolyModel):
    url = db.StringProperty()
    inviteDate = db.StringProperty()
    expirationDate = db.StringProperty()
    code = db.StringProperty()
    person = db.ReferenceProperty(Person)
    exam = db.ReferenceProperty(Exam)

    def short(self):
        return {'id': self.key().id_or_name()}

    def details(self):
        return {'id': self.key().id_or_name(),
                'url': self.url,
                'inviteDate': self.inviteDate,
                'expirationDate': self.expirationDate,
                'code': self.code,
                'person': self.person.key().id_or_name(),
                'exam': self.exam.key().id_or_name()}

    def parse(self, exam, code, url, invite_date, expiration_date):
        self.code = code
        self.url = url
        self.inviteDate = invite_date
        self.expirationDate = expiration_date
        self.exam = exam

    def parse_dict(self, data_dict):
        self.code = data_dict['code']
        self.url = data_dict['url']
        self.inviteDate = data_dict['inviteDate']
        self.expirationDate = data_dict['expirationDate']
        self.exam = Exam.get_by_key_name(data_dict['exam'])
        self.person = Person.get_by_id(data_dict['person'])

    @staticmethod
    def random_code(date, person_id, exam_id):
        hashing_tool = hashlib.md5()
        hashing_tool.update(date + str(person_id) + str(exam_id))
        return hashing_tool.hexdigest()


#Modelclass AcceptedInvite
class AcceptedInvite(Invite):
    """
    Sub-class used to allow easy filtering in the views on accepted invites,
    without changing the (final) score classes since they rely on invite's
    information.
    """
    pass


#Modelclass OpenInvite
class OpenInvite(Invite):
    """"
    Sub-class used to create further distinction between invite types. This
    way, only open invites can be fetched directly, rather than fetching all
    (base) Invites and filtering them manually.
    """
    pass


#Modelclass FinalScore
class FinalScore(polymodel.PolyModel):
    result = db.FloatProperty()
    max_result = db.FloatProperty()
    result_percentage = db.FloatProperty()
    passed = db.BooleanProperty()
    date = db.StringProperty()
    time_taken = db.StringProperty()
    version = db.IntegerProperty()
    invite = db.ReferenceProperty(Invite)
    score_objects = db.ListProperty(db.Key, name="score_object_set")

    def short(self):
        return {"id": self.key().id_or_name()}

    def details(self):
        return {"id": self.key().id_or_name(),
                "result": self.result,
                "max_result": self.max_result,
                "passed": self.passed,
                "date": self.date,
                "time_taken": self.time_taken,
                "invite": self.invite.key().id_or_name(),
                "version": self.version,
                "result_percentage": self.result_percentage,
                "score_objects": map(lambda score_object: score_object.id_or_name(), self.score_objects)}

    def parse(self, data_dict):
        self.result = data_dict['result']
        self.max_result = data_dict['max_result']
        self.result_percentage = data_dict['result_percentage']
        self.passed = data_dict['passed']
        self.date = data_dict['date']
        self.time_taken = data_dict['time_taken']
        #self.version = data_dict['version']  # TODO: version
        self.invite = data_dict['invite']
        self.score_objects = data_dict['score_objects']

    def check_result_validity(self, result):
        if result is not None:
            try:
                value = float(result)
            except ValueError:
                return errors.InvalidResultValueError(result)
            if not math.isnan(value):
                return
            else:
                return errors.InvalidResultValueError(result)
        else:
            return errors.InvalidResultValueError(result)

    def check_max_result_validity(self, max_result, result):
        try:
            result_value = float(result)
            if max_result is not None:
                value = float(max_result)
                if not math.isnan(value) and value > 0 and value >= float(result_value):
                    return
                else:
                    return errors.InvalidMaxResultValueError(max_result, result_value)
            else:
                return errors.InvalidMaxResultValueError(max_result, result_value)
        except ValueError:
            return errors.InvalidMaxResultValueError(max_result, result_value)

    def check_result_percentage_validity(self, result_percentage, result, max_result):
        result_errors = self.check_max_result_validity(max_result, result)
        if result_errors is not None:
            return result_errors
        if result_percentage is not None:
            try:
                value = float(result_percentage)
            except ValueError:
                return errors.InvalidResultPercentageError(result_percentage, max_result, result)
            if not math.isnan(value) and value >= 0:
                return
            else:
                return errors.InvalidResultPercentageError(result_percentage, max_result, result)
        else:
            return errors.InvalidResultPercentageError(result_percentage, max_result, result)

    def check_passed_validity(self, passed):
        if not isinstance(passed, bool):
            return errors.InvalidPassedValueError(passed)

    def check_date_validity(self, date):
        if date is not None:
            try:
                time.strptime(date, "%x")
            except ValueError:
                return errors.InvalidDateError(date)
        else:
            return errors.InvalidDateError(date)

    def check_time_taken_validity(self, time_taken):
        if time_taken is not None:
            try:
                time.strptime(time_taken, "%H:%M:%S")
            except ValueError:
                try:
                    time.strptime(time_taken, "%M:%S")
                except ValueError:
                    return errors.InvalidTimeTakenValueError(time_taken)
        else:
            return errors.InvalidTimeTakenValueError(time_taken)

    def check_invite_reference_validity(self, invite):
        if invite is None or not invite.is_saved():
            return errors.InvalidInviteReferenceError(invite)
        else:
            if Invite.get_by_key_name(invite.key().id_or_name()) is None:
                return errors.InvalidInviteReferenceError(invite)

    def check_score_objects_validity(self, score_key_list):
        error_list = []
        if score_key_list is not None and len(filter(None, score_key_list)) > 0:
            for score_key in score_key_list:
                if score_key is not None and isinstance(score_key, db.Key):
                    continue
                else:
                    error_list.append(errors.InvalidScoreKeyError(score_key))
            if len(filter(None, error_list)) > 0:
                return errors.InvalidScoreKeyListError(score_key_list, error_list)
        else:
            return errors.InvalidScoreKeyListError(score_key_list)

    def checkDataValidity(self):
        error_list = [self.check_result_validity(self.result),
                      self.check_max_result_validity(self.max_result, self.result),
                      self.check_result_percentage_validity(self.result_percentage, self.result, self.max_result),
                      self.check_passed_validity(self.passed),
                      self.check_date_validity(self.date),
                      self.check_time_taken_validity(self.time_taken),
                      self.check_invite_reference_validity(self.invite),
                      self.check_score_objects_validity(self.score_objects)]
        if len(filter(None, error_list)) != 0:
            return errors.InvalidDataError(error_list)

    def create_report_data(self):
        invite_person = self.invite.person
        data = [["Testresultaten"], ["Het resultaat van de test wordt hieronder weergegeven"],
                [""], ["Algemene informatie over de kandidaat:"],
                ["Kandidaat: ", invite_person.name]]
        if invite_person.age is not None:
            data.append(["Leeftijd: ", invite_person.age])
        else:
            data.append(["Leeftijd: ", "onbekend"])
        if invite_person.education_level is not None:
            data.append(["Opleidingsniveau: ", invite_person.education_level])
        else:
            data.append(["Opleidingsniveau: ", "onbekend"])
        if invite_person.education_type is not None:
            data.append(["Studierichting: ", invite_person.education_type])
        else:
            data.append(["Studierichting: ", "onbekend"])
        data.append([""])
        data.append(["Informatie over de test:"])
        data.append(["Datum van voltooiing: ", self.date])
        data.append(["Test voltooid in: ", self.time_taken])
        data.append([""])
        data.append(["Totaal aantal vragen: ", len(self.score_objects)])
        data.append(["Totaal verdiende punten: ", str(self.result)])
        data.append(["Totaal maximaal te behalen punten: ", str(self.max_result)])

        data.append(["Totale score: ", str(self.result_percentage) + "%"])
        data.append([""])
        return data


#Modelclass MultipleChoiceFinalScore
class FinalMultipleChoiceScore(FinalScore):
    """
    @knowledge_area_json properties - These are all string properties that will contain the data from a dictionary in
    JSON format, since the datastore does not support direct dictionary storage. Example of contents:
    '[{"Math": 28.5}, {"Languages": 12.2}]'
    """
    knowledge_area_earned_json = db.StringProperty()
    knowledge_area_max_values_json = db.StringProperty()
    knowledge_area_percentages_json = db.StringProperty()
    total_earned_for_all_knowledge_areas = db.FloatProperty()
    total_max_for_all_knowledge_areas = db.FloatProperty()
    total_percentage_for_all_knowledge_areas = db.FloatProperty()
    average_percentage_for_all_knowledge_areas = db.FloatProperty()

    def details(self):
        superDict = super(FinalMultipleChoiceScore, self).details()
        selfDict = self.parse_jsons_to_dict(self.knowledge_area_earned_json,
                                            self.knowledge_area_max_values_json,
                                            self.knowledge_area_percentages_json)
        selfDict["average_percentage_for_all_knowledge_areas"] = self.average_percentage_for_all_knowledge_areas
        return dict(superDict.items() + selfDict.items())

    def checkDataValidity(self):
        error_list = []
        invalid_data_error = super(FinalMultipleChoiceScore, self).checkDataValidity()
        if invalid_data_error is not None:
            error_list.extend(invalid_data_error.error_list)
        error_list.extend([self.check_knowledge_area_earned_json_validity(self.knowledge_area_earned_json),
                           self.check_knowledge_area_max_values_json_validity(self.knowledge_area_earned_json,
                                                                              self.knowledge_area_max_values_json),
                           self.check_knowledge_area_percentages_json_validity(self.knowledge_area_earned_json,
                                                                               self.knowledge_area_max_values_json,
                                                                               self.knowledge_area_percentages_json),
                           self.check_average_percentage_for_all_knowledge_areas_validity(
                               self.average_percentage_for_all_knowledge_areas)])

        if len(filter(None, error_list)) != 0:
            return errors.InvalidDataError(error_list)

    def check_average_percentage_for_all_knowledge_areas_validity(self, average_percentage_for_all_knowledge_areas):
        if average_percentage_for_all_knowledge_areas is not None:
            try:
                float_value = float(average_percentage_for_all_knowledge_areas)
                if not math.isnan(float_value) and not float_value > 100.0:
                    return
                else:
                    return errors.InvalidAveragePercentageForAllKnowledgeAreasError(
                        average_percentage_for_all_knowledge_areas)
            except ValueError:
                return errors.InvalidAveragePercentageForAllKnowledgeAreasError(
                    average_percentage_for_all_knowledge_areas)
        else:
            return errors.InvalidAveragePercentageForAllKnowledgeAreasError(average_percentage_for_all_knowledge_areas)

    @staticmethod
    def check_knowledge_area_json_string_validity(knowledge_area_json):
        """
        This method checks if a string that represents JSON data will parse into
        a dictionary that contains (valid, non-empty) strings as keys and a float
        as value (x != 0.0)
        """
        if knowledge_area_json is not None:
            try:
                dictionary = json.loads(knowledge_area_json)
                if dictionary is not None and isinstance(dictionary, dict):
                    for key in dictionary.keys():
                        if key is not None and key is not '':
                            try:
                                item = dictionary[key]
                                if item is not None and item is not "" and not math.isnan(item):
                                    try:
                                        float_item = float(item)
                                    except ValueError:
                                        return errors.InvalidKnowledgeAreaJsonStringError(
                                            knowledge_area_json)
                                else:
                                    return errors.InvalidKnowledgeAreaJsonStringError(knowledge_area_json)
                            except KeyError:
                                return errors.InvalidKnowledgeAreaJsonStringError(
                                    knowledge_area_json)
                        else:
                            return errors.InvalidKnowledgeAreaJsonStringError(knowledge_area_json)
                else:
                    return errors.InvalidKnowledgeAreaJsonStringError(knowledge_area_json)
            except ValueError:
                return errors.InvalidKnowledgeAreaJsonStringError(knowledge_area_json)
        else:
            return errors.InvalidKnowledgeAreaJsonStringError(knowledge_area_json)

    def check_knowledge_area_earned_json_validity(self, knowledge_area_earned_json):
        knowledge_area_earned_json_error = self.check_knowledge_area_json_string_validity(knowledge_area_earned_json)
        if knowledge_area_earned_json_error is not None:
            return knowledge_area_earned_json_error

    def check_knowledge_area_max_values_json_validity(self, knowledge_area_earned_json, knowledge_area_max_values_json):
        knowledge_area_earned_json_error = self.check_knowledge_area_earned_json_validity(knowledge_area_earned_json)
        if knowledge_area_earned_json_error is not None:
            return knowledge_area_earned_json_error
        knowledge_area_max_json_error = self.check_knowledge_area_json_string_validity(knowledge_area_max_values_json)
        if knowledge_area_max_json_error is not None:
            return knowledge_area_max_json_error

        earned_loaded = json.loads(knowledge_area_earned_json)
        max_loaded = json.loads(knowledge_area_max_values_json)
        for key in earned_loaded.keys():
            if key in max_loaded and max_loaded[key] >= earned_loaded[key]:
                continue
            else:
                return errors.InvalidKnowledgeAreaMaxJsonError(knowledge_area_earned_json,
                                                               knowledge_area_max_values_json)

    def check_knowledge_area_percentages_json_validity(self, knowledge_area_earned_json, knowledge_area_max_values_json,
                                                       knowledge_area_percentages_json):
        knowledge_area_max_json_error = self.check_knowledge_area_max_values_json_validity(
            knowledge_area_earned_json, knowledge_area_max_values_json)
        if knowledge_area_max_json_error is not None:
            return knowledge_area_max_json_error
        knowledge_area_percentage_json_error = self.check_knowledge_area_json_string_validity(
            knowledge_area_percentages_json)
        if knowledge_area_percentage_json_error is not None:
            return knowledge_area_percentage_json_error

        earned_loaded = json.loads(knowledge_area_earned_json)
        max_loaded = json.loads(knowledge_area_max_values_json)
        percentage_loaded = json.loads(knowledge_area_percentages_json)
        for key in earned_loaded.keys():
            if key in max_loaded and key in percentage_loaded and round(
                    float((100 / max_loaded[key]) * earned_loaded[key]), 2) == percentage_loaded[key]:
                continue
            else:
                return errors.InvalidKnowledgeAreaPercentageJsonError(knowledge_area_earned_json,
                                                                      knowledge_area_max_values_json,
                                                                      knowledge_area_percentages_json)


    @staticmethod
    def parse_jsons_to_dict(knowledge_area_earned_json, knowledge_area_max_values_json,
                            knowledge_area_percentages_json):
        data_dict = {"knowledge_area_earned": json.loads(knowledge_area_earned_json),
                     "knowledge_area_max_values": json.loads(knowledge_area_max_values_json),
                     "knowledge_area_percentages": json.loads(knowledge_area_percentages_json)}
        return data_dict

    @staticmethod
    def parse_dict_to_jsons(knowledge_area_earned_dict, knowledge_area_max_values_dict,
                            knowledge_area_percentages_dict):
        data_dict = {"knowledge_area_earned": json.dumps(knowledge_area_earned_dict),
                     "knowledge_area_max_values": json.dumps(knowledge_area_max_values_dict),
                     "knowledge_area_percentages": json.dumps(knowledge_area_percentages_dict)}
        return data_dict

    def parse(self, data_dict):
        super(FinalMultipleChoiceScore, self).parse(data_dict)
        json_dict = self.parse_dict_to_jsons(data_dict["knowledge_area_earned_dict"],
                                             data_dict["knowledge_area_max_values_dict"],
                                             data_dict["knowledge_area_percentages_dict"])
        self.knowledge_area_earned_json = json_dict["knowledge_area_earned"]
        self.knowledge_area_max_values_json = json_dict["knowledge_area_max_values"]
        self.knowledge_area_percentages_json = json_dict["knowledge_area_percentages"]
        self.total_earned_for_all_knowledge_areas = data_dict["total_earned_for_all_knowledge_areas"]
        self.total_max_for_all_knowledge_areas = data_dict["total_max_for_all_knowledge_areas"]
        self.total_percentage_for_all_knowledge_areas = data_dict["total_percentage_for_all_knowledge_areas"]
        self.average_percentage_for_all_knowledge_areas = data_dict["average_percentage_for_all_knowledge_areas"]


    def create_report_data(self):
        super_data = super(FinalMultipleChoiceScore, self).create_report_data()
        data = [
            [""],
            ["Totaal verdiende punten\nvoor kennisgebieden: ", str(self.total_earned_for_all_knowledge_areas)],
            ["Totaal maximaal te behalen\npunten voor kennisgebieden: ", str(self.total_max_for_all_knowledge_areas)],
            ["Totaal percentage\nvoor kennisgebieden: ", str(self.total_percentage_for_all_knowledge_areas) + " %"],
            ["Merk op dat de totaal verdiende/maximale waarde niet hetzelfde is als de totaal verdiende/maximale \n"
             "waarde voor alle kennisgebieden."],
            [""],
            ["Hieronder staat een overzicht met daarin per kennisgebied het behaalde percentage:"],
            ["Kennisgebied:", "Behaalde score:", "Maximale score:", "Percentage:"]
        ]

        data_dict = FinalMultipleChoiceScore.parse_jsons_to_dict(self.knowledge_area_earned_json,
                                                                 self.knowledge_area_max_values_json,
                                                                 self.knowledge_area_percentages_json)

        for key in data_dict["knowledge_area_percentages"].keys():
            data.append([key + ": ", str(data_dict["knowledge_area_earned"][key]),
                         str(data_dict["knowledge_area_max_values"][key]),
                         str(data_dict["knowledge_area_percentages"][key]) + "%"])
        data.append([""])
        data.append(["Gemiddelde score voor\nalle kennisgebieden: ",
                     str(self.average_percentage_for_all_knowledge_areas) + "%"])
        return super_data, data, data_dict


#Modelclass Score
class Score(polymodel.PolyModel):
    invite = db.ReferenceProperty(Invite)
    correct_answers = db.ListProperty(db.Key, name="correct")
    earned_value = db.FloatProperty()
    time_taken = db.StringProperty()
    date = db.StringProperty()

    def short(self):
        return {'id': self.key().id()}

    def details(self):
        return {'id': self.key().id(),
                'invite': self.invite.key().id_or_name(),
                'correct_answers': map(lambda correct_key: {'id': correct_key.id_or_name()}, self.correct_answers),
                'earned_value': self.earned_value,
                'time_taken': self.time_taken,
                'date': self.date}

    def parse_base(self, correct_answer_objects, earned_value, invite_object, time_string, date):
        self.correct_answers = map(lambda correct_answer_object: correct_answer_object.key(), correct_answer_objects)
        self.earned_value = earned_value
        self.invite = invite_object
        self.time_taken = time_string
        self.date = date


#Modelclass OpenQuestionScore
class OpenQuestionScore(Score):
    def parse(self, correct_answer_objects, earned_value, invite, time, date):
        self.parse_base(correct_answer_objects, earned_value, invite, time, date)


#Modelclass MBTIScore
class MBTIScore(Score):
    mbti_personality_character = db.StringProperty()
    mbti_personality_value_earned = db.FloatProperty()

    def details(self):
        return {"mbti_personality_character": self.mbti_personality_character,
                "mbti_personality_value_earned": self.mbti_personality_value_earned}.update(
            super(MBTIScore, self).details())

    def parse(self, correct_answer_objects, earned_value, mbti_personality_character,
              mbti_personality_value_earned, invite, time, date):
        self.mbti_personality_character = mbti_personality_character
        self.mbti_personality_value_earned = mbti_personality_value_earned
        self.parse_base(correct_answer_objects, earned_value, invite, time, date)


#Modelclass MultipleChoiceScore
class MultipleChoiceScore(Score):
    knowledge_area_score_earned_json = db.StringProperty()
    knowledge_area_score_max_json = db.StringProperty()

    def details(self):
        super_dict = super(MultipleChoiceScore, self).details()
        self_dict = {"knowledge_area_earned_scores": json.dumps(self.knowledge_area_score_earned_json),
                     "knowledge_area_max_scores": json.dumps(self.knowledge_area_score_max_json)}
        return dict(super_dict.items() + self_dict.items())

    def parse(self, correct_answer_objects, earned_value, knowledge_area_earned_scores_dict,
              knowledge_area_max_scores_dict, invite, date, time):
        self.knowledge_area_score_earned_json = json.dumps(knowledge_area_earned_scores_dict)
        self.knowledge_area_score_max_json = json.dumps(knowledge_area_max_scores_dict)
        self.parse_base(correct_answer_objects, earned_value, invite, time, date)

    def parse_knowledge_area_score_json_to_dict(self, json_string):
        data_dict = json.loads(json_string)
        return data_dict


#Modelclass AnsweredQuestion
class AnsweredQuestion(db.Model):
    question = db.ReferenceProperty(Question)
    invite = db.ReferenceProperty(Invite)
    givenAnswers = db.ListProperty(db.Key, name="givenanswer_set")

    def short(self):
        return {"id": self.key().id_or_name()}

    def details(self):
        return {"id": self.key().id_or_name(),
                "question": self.question.key().id_or_name(),
                "invite": self.invite.key().id_or_name(),
                "givenAnswers": self.parse_given_answers_key_collection_to_id_collections(self.givenAnswers)}

    def parse_short(self, data_dict):
        if data_dict is not None and len(data_dict) > 0:
            try:
                self.question = Question.get_by_id(int(data_dict["question"]))
                self.invite = Invite.get_by_key_name(data_dict["invite"])
                self.givenAnswers = self.parse_given_answers_id_collection_to_key_collections(
                    data_dict["givenAnswers"])
            except KeyError:
                raise errors.InvalidDataForDictionaryError(data_dict)
        else:
            raise errors.InvalidDataForDictionaryError(data_dict)

    def parse(self, data_dict):
        if data_dict is not None and len(data_dict) > 0:
            try:
                self.question = Question.get_by_id(int(data_dict["question"]["id"]))
                self.invite = Invite.get_by_key_name(data_dict["invite"]["id"])
                self.givenAnswers = self.parse_given_answers_id_collection_to_key_collections(
                    map(lambda given_answer_object: given_answer_object["id"], data_dict["givenAnswers"]))
            except KeyError:
                raise errors.InvalidDataForDictionaryError(data_dict)
        else:
            raise errors.InvalidDataForDictionaryError(data_dict)


    @staticmethod
    def parse_given_answers_key_collection_to_id_collections(given_answer_keys_list):
        id_dictionaries_list = []
        if given_answer_keys_list is not None:
            for given_answer_key in given_answer_keys_list:
                if isinstance(given_answer_key, db.Key) and given_answer_key.has_id_or_name():
                    id_dictionaries_list.append({"id": given_answer_key.id_or_name()})
            return id_dictionaries_list
        else:
            return []

    @staticmethod
    def parse_given_answers_id_collection_to_key_collections(given_answers_id_list):
        key_list = []
        if given_answers_id_list is not None:
            for given_id in given_answers_id_list:
                try:
                    int_id = int(given_id)
                    answer_object = Answer.get_by_id(int_id)
                    if answer_object is not None:
                        key_list.append(answer_object.key())
                except (ValueError, TypeError):
                    continue

        return key_list

    @staticmethod
    def check_question_reference_validity(question):
        if question is None or not question.is_saved():
            return errors.InvalidQuestionReferenceError(question)
        elif Question.get_by_id(question.key().id_or_name()) is None:
            return errors.InvalidQuestionReferenceError(question)

    @staticmethod
    def check_given_answer_reference_list_validity(given_answer_key_list):
        error_list = []
        if given_answer_key_list is not None:
            for key in given_answer_key_list:
                if key is None or not isinstance(key, db.Key):
                    error_list.append(errors.InvalidGivenAnswerReferenceError(key))
            if len(filter(None, error_list)) > 0:
                return error_list
        else:
            return errors.InvalidGivenAnswersReferenceListError(given_answer_key_list)

    @staticmethod
    def check_invite_reference_validity(invite):
        if invite is None:
            return errors.InvalidInviteReferenceError(invite)
        elif Invite.get_by_key_name(invite.key().id_or_name()) is None:
            return errors.InvalidInviteReferenceError(invite)

    def checkDataValidity(self):
        error_list = [AnsweredQuestion.check_question_reference_validity(self.question),
                      AnsweredQuestion.check_given_answer_reference_list_validity(self.givenAnswers),
                      AnsweredQuestion.check_invite_reference_validity(self.invite)]
        if len(filter(None, error_list)) != 0:
            return errors.InvalidDataError(error_list)
