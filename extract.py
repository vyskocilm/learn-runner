from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
    
    def _noop (self, *args, **kwargs):
        return

    def __init__ (self):
        self._handle_starttag = self._find_div_id_questions
        self._handle_endtag = self._noop
        self._handle_data = self._noop
        super ().__init__ ()

        self._correct_answer = False

        self._questions = list ()

    def handle_starttag(self, tag, attrs):
        return self._handle_starttag (tag, attrs)

    def handle_endtag(self, tag):
        return self._handle_endtag (tag)

    def handle_data(self, data):
        return self._handle_data (data)

    def _find_div_id_questions (self, tag, attrs):
        if (tag == "div" and ("id", "questions") in attrs):
            self._handle_starttag = self._find_question_b

    def _find_question_b (self, tag, attrs):
        if (tag == "b"):
            self._questions.append ({"question" : "", "answers" : []})

            self._handle_data = self._print_question
            self._handle_starttag = self._find_correct_answer
            self._correct_answer = False
        else:
            self._handle_data = self._noop

    def _find_correct_answer (self, tag, attrs):
        if (tag == "div" and ("class", "row correct-answer green inverted") in attrs):
            self._correct_answer = True
        elif (tag == "div" and ("class", "row") in attrs):
            self._correct_answer = False
        self._handle_starttag = self._find_p_fifteen

    def _find_p_fifteen (self, tag, attrs):
        if (tag == "p" and ("class", "fifteen wide column   ") in attrs):
            self._handle_data = self._print_answer
        elif (tag == "div" and ("class", "ui grid") in attrs):
            self._handle_starttag = self._find_question_b

    def _print_answer (self, data):
        answer = data.strip ().replace ('\n', '')
        if answer [-1] == ',' or answer [-1] == '.':
            answer = answer [:-1]
        self._questions [-1] ["answers"].append (
            {"correct" : self._correct_answer,
             "answer" : answer})
        self._handle_data = self._noop
        self._handle_starttag = self._find_correct_answer

    def _print_question (self, data):
        self._questions [-1]["question"] = data
        self._handle_data = self._noop

parser = MyHTMLParser()
with open ("Seznam testových otázek ke zkoušce odborné způsobilosti | ZbraněKvalitně.cz.html", "r") as fp:
    parser.feed (data=fp.read())

import json, sys

json.dump (parser._questions, sys.stdout, ensure_ascii=False, indent=4)
