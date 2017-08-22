import json

from fractions import Fraction
from collections import namedtuple

class Question:

    def __init__ (self, question, answers):
        self._question = question
        self._answers = answers
        self._correct = sum ((a["correct"] for a in self._answers))

    @property
    def question (self):
        return self._question

    @property
    def answers (self):
        return self._answers

    def aiter (self):
        return iter ((a["text"], a["correct"]) for a in self._answers)

    def result (self, attempts):
        inc = Fraction (1, self._correct)
        ret = Fraction (0)

        for at in attempts:
            if self._answers [at] ["correct"]:
                ret += inc
            else:
                ret -= inc

        if ret < 0:
            return Fraction (0)
        return ret

    def __eq__ (self, oQuestion):
        if self._question != oQuestion.question:
            return False

        for (correct1, text1), (correct2, text2) in zip (self.aiter (), oQuestion.aiter ()):

            if correct1 != correct2:
                return False
            if text1 != text2:
                return False

        return True

class QuestionList:

    def __init__ (self, questions=None):
        if questions is not None:
            self._questions = questions
        else:
            self._questions = questions

    @classmethod
    def load (cls, questions_fp):
        questions = list ()
        q = json.load (questions_fp)
        for item in q:
            questions.append (
                Question (item ["question"],
                          item ["answers"])
                )
        return cls (questions)

    def save (self, questions_fp):
        #TODO JSON decoder
        lst = [{"question" : q.question, "answers" : q.answers} for q in self._questions]
        json.dump (lst, questions_fp)

    def __len__ (self):
        return len (self._questions)

    def __eq__ (self, oQuestionList):
        for q1, q2 in zip (self._questions, oQuestionList._questions):
            if q1 != q2:
                return False

        return True

def test_Question ():

    q = Question (
        "What is the air-speed velocity of an unladen swallow?",
        ({"correct" : False, "text" : "I don't know"},
         {"correct" : True, "text" : "What do you mean? An African or European swallow?"},
         {"correct" : False, "text" : "Norwegian Blue"}
        ))

    assert q
    assert q.question == "What is the air-speed velocity of an unladen swallow?"
    assert q.result ((0, )) == Fraction (0)
    assert q.result ((0, 2)) == Fraction (0)
    assert q.result ((1, 2)) == Fraction (0)
    assert q.result ((1, )) == Fraction (1, 1)

HistoryItem = namedtuple ("HistoryItem", "date, duration, rate")

class QuestionHistory:

    def __init__ (self, idx, history):
        self._idx = idx
        self._history = history

    @property
    def idx (self):
        return idx

    @property
    def history (self):
        return history

    def __iter__ (self):
        return iter (self._history)

class Stats:

    def __init__ (self, stats):
        self._stats = stats

    @classmethod
    def load (cls, json_fp):

        def js2f (d):
            """convert json to Fraction"""
            return Fraction (
                d.get ("rate_numerator", 0),
                d.get ("rate_denominator", 1))

        js = json.load (json_fp)
        stats = dict ()
        for d in js:
            idx = d ["question_id"]
            history = [HistoryItem (
                    i["date"],
                    i["duration"],
                    js2f (i)) for i in d["history"]]
            stats [idx] = QuestionHistory (0, history)

        return cls (stats)

    def save (self, json_fp):

        stats = list ()
        for idx, history in self._stats.items ():
            h = [{
                "date" : i.date,
                "duration" : i.duration,
                "rate_numerator" : i.rate.numerator,
                "rate_denominator" : i.rate.denominator} for i in history]
            stats.append ({"question_id" : idx, "history" : h})

        json.dump (stats, json_fp)

    def __eq__ (self, oself):
        for (idx1, hist1), (idx2, hist2) in zip (self._stats.items (), oself._stats.items ()):
            if idx1 != idx2:
                return False
            if hist1._history != hist2._history: #TODO: proper __eq__ for _history class
                return False

        return True

def test_Questions ():

    from tempfile import mkstemp
    from os import close, unlink

    q0 = Question (
        "What is the air-speed velocity of an unladen swallow?",
        ({"correct" : False, "text" : "I don't know"},
         {"correct" : True, "text" : "What do you mean? An African or European swallow?"},
         {"correct" : False, "text" : "Norwegian Blue"}
        ))

    q1 = Question (
        "What is the capital of Assyria",
        ({"correct" : False, "text" : "I don't know"},
         {"correct" : True, "text" : "Assur"},
         {"correct" : True, "text" : "Dur-Shakurrin"},
         {"correct" : True, "text" : "Ekallatum"},
         {"correct" : True, "text" : "Harran"},
         {"correct" : True, "text" : "Carchemish"},
         {"correct" : True, "text" : "Tell Leilan"},
         {"correct" : True, "text" : "Kar-Tukuti-Ninurta"},
        ))

    qlst = QuestionList ((q0, q1))
    
    fd, name = mkstemp ()
    with open (name, "wt") as fp:
        qlst.save (fp)

    qlst2 = None
    with open (name, "rt") as fp:
        qlst2 = QuestionList.load (fp)

    close (fd)
    unlink (name)

    assert qlst == qlst2

def test_Stats ():

    from tempfile import mkstemp
    from os import close, unlink

    _stats = {
        0   :   QuestionHistory (0, [HistoryItem (1234, 10, Fraction (1)), HistoryItem (1255, 5, Fraction (1,2))]),
        1   :   QuestionHistory (1, [HistoryItem (1236, 10, Fraction ()), HistoryItem (1255, 5, Fraction (1, 3))]),
    }

    stats = Stats (_stats)

    fd, name = mkstemp ()
    with open (name, "wt") as fp:
        stats.save (fp)

    stats2 = None
    with open (name, "rt") as fp:
        stats2 = Stats.load (fp)

    close (fd)
    unlink (name)

    assert stats == stats2

QUESTIONS = """
[
    {
        "question": "blablabla",
        "answers" : [
            {
                "correct" : True,
                "text" : "ham spam ham spam"
            },
            {
                "correct" : False,
                "test" : "Use Perl, Luke!"
            }
        ]
    }
]
"""

STATS = """
[
    {
        "question_id" : 0,
        "history" : [
            {
                "date" : 1234567,
                "duration" : 123,
                "rate" : 1.0
            },
            {
                "date" : 1234999,
                "duration" : 1,
                "rate" : 0.0
            },
        ]
    }
]
"""
