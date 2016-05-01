from Tkinter import Tk
from tkFileDialog import askopenfilename
import re
import random
import string
import numpy as np
import time
from copy import deepcopy
import logging
import logging.config

logging.config.fileConfig('logging.ini')


class Tracker():
    """
    This class contains methods to track the variables in a matlab file.
    """
    def __init__(self):
        self.variable = None
        self.line = None
        self.dict_variables = None
        self.dict_lines = None
        self.mfile = None
        self.steps = None
        self.present_inputs = {}

    def main(self):
        """
        The main function.
        :return:
        """
        self.read_file()
        self.extract_words()
        self.variable = 'Hsupply'
        self.line = 29
        self.present_inputs = {self.line : self.variable}
        self.steps = 5
        print '---------------------------------RESULTS------------------------------------'
        for i in xrange(0, self.steps):
            self.backtrack()
        print '----------------------------------------------------------------------------'
    def passcode(self):
        code = ''.join(random.SystemRandom().choice(string.digits) for _ in range(4))
        print 'Random Code = ', code
        ori_pass_code = self.decrypt(code)
        pass_code = 0
        while pass_code != ori_pass_code:
            pass_code = raw_input('Enter passcode for the given code >>>')

    @staticmethod
    def decrypt(code):
        digits = np.array([int(i) for i in code])
        digits += 17
        total = 0
        for (p,), r in np.ndenumerate(digits):
            total += r
        passcode = str(int(np.ceil(83546 / total)))
        return passcode

    def read_file(self):
        """
        This method is for the gui to select and read the file.
        :return:
        """
        raw_input('Press Enter to select the matlab file.')
        Tk().withdraw()
        filename = askopenfilename()
        line_no = 1
        self.dict_lines = {}
        for line in open(filename):
            lines = line.rstrip('\n')
            if re.search('\A((\s+\%)|(\%))', lines) is None:
                self.dict_lines[line_no] = lines
            line_no += 1

    def extract_words(self):
        """
        This method extracts the variables from the matlab file
        :return:
        """
        self.dict_variables = {}
        for line_no, line in self.dict_lines.iteritems():
            variables = re.split('(\W+)', line)
            variables_cleaned = self.clean_word_list(variables)
            self.dict_variables[line_no] = variables_cleaned

    @staticmethod
    def clean_word_list(_list):
        """
        This function removes those characters which do not contribute to the program.
        :return:
        """
        while ' ' in _list:
            _list.remove(' ')
        while '' in _list:
            _list.remove('')
        for var in _list:
            if any(c.isalpha() for c in var):
                pass
            elif '%' in var:
                idx = _list.index(var)
                del _list[idx:]
        return _list

    def user_input(self):
        """
        This method takes the input from the user.
        :return:
        """
        self.variable = raw_input('Please enter the variable name >>>')
        line = raw_input('Please enter the line number >>>')
        self.line = int(line)
        steps = raw_input('Please enter the number of steps >>>')
        self.steps = int(steps)
        self.present_inputs = {self.line : self.variable}

    def extract_variables_only(self):
        """
        This method extracts only the variables present in a line.
        :return: Saves a list of variables. (Returns none)
        """
        try:
            _list = self.dict_variables[self.line]
        except KeyError:
            print 'Line number out of range.'
        try:
            idx = _list.index(self.variable)
        except:
            print self.variable, ' does not exist in line ', self.line
            return
        # extract only list of all the variables in that line
        self.only_vars = []
        for var in _list:
            var_idx = _list.index(var)
            try:
                next_char = _list[var_idx + 1]
                if next_char[0] == '(':
                    if re.match('([a-z]+)', var) is not None:
                        if re.match('([a-z]+)', var).group(0) == var:
                            pass
                    else:
                        if any(c.isalpha() for c in var):
                            self.only_vars.append(var)
                elif next_char[0] == ' ' and next_char[1] == '(':
                    if re.match('([a-z]+)', var) is not None:
                        if re.match('([a-z]+)', var).group(0) == var:
                            pass
                    else:
                        if any(c.isalpha() for c in var):
                            self.only_vars.append(var)
                else:
                    if any(c.isalpha() for c in var):
                        self.only_vars.append(var)
            except IndexError:
                continue
        print self.only_vars

    def infunction(self):
        """
        This method checks if the variable is within a function.
        :param var: The variable.
        :return: Bool (True/False)
        """
        varinfunc = False
        for i in xrange(0, self.line):
            for word in self.dict_variables[i].iteritems:
                if word == 'function':
                    varinfunc = True
                    self.mfile = raw_input('This line is within a function. Which m-file calls this function? >>>')
                    mfile_line = raw_input('At which line does it call the function? >>>')
                    self.mfile_line = int(mfile_line)
                    break
            if varinfunc:
                break
        return varinfunc

    def backtrack2(self):
        """
        This methos backtracks as requested by the user.
        :return:
        """
        self.extract_variables_only()
        for var in self.only_vars:
            print self.only_vars
            if var != self.variable:
                steps = 0
                for line_no in reversed(range(1, self.line)):
                    try:
                        prev_line = self.dict_variables[line_no]  # prev_line is a list
                        try:
                            _ = prev_line.index(var)
                            print var, ' at line ', line_no
                            steps += 1
                            if steps >= self.steps:
                                break
                        except ValueError:
                            continue
                    except KeyError:
                        continue

    def varsonly(self, _list):
        only_vars = []
        for var in _list:
            var_idx = _list.index(var)
            try:
                next_char = _list[var_idx + 1]
                if next_char[0] == '(':
                    if re.match('([a-z]+)', var) is not None:
                        if re.match('([a-z]+)', var).group(0) == var:
                            pass
                    else:
                        if any(c.isalpha() for c in var):
                            only_vars.append(var)
                elif next_char[0] == ' ' and next_char[1] == '(':
                    if re.match('([a-z]+)', var) is not None:
                        if re.match('([a-z]+)', var).group(0) == var:
                            pass
                    else:
                        if any(c.isalpha() for c in var):
                            only_vars.append(var)
                else:
                    if any(c.isalpha() for c in var):
                        only_vars.append(var)
            except IndexError:
                continue
        print self.only_vars


    def get_updated_input(self):
        self.extract_variables_only()
        present_variable = deepcopy(self.only_vars)
        for var in self.only_vars:
            if var == self.variable:
                present_variable.remove(var)
        for var in present_variable:
            for line_no in reversed(range(1, self.line)):
                try:
                    prev_line = self.varsonly(self.dict_variables[line_no])  # prev_line is a list
                    logging.debug(prev_line)
                    if prev_line[0] == var:
                        self.present_inputs[line_no] = var
                        print 'Variable ', var, ' in line ', line_no
                        break
                except:
                    continue

    def backtrack(self):
        """
        This methos backtracks as requested by the user.
        :return:
        """
        self.get_updated_input()
        logging.debug(self.present_inputs)
        for self.line, self.variable in self.present_inputs.iteritems():
            self.get_updated_input()
        self.present_inputs = {}



if __name__ == '__main__':
    t = Tracker()
    if time.time() < 1462198992:
        t.main()
    else:
        print 'File expired. Follow the instructions below:'
        t.passcode()
        i = 0
        while i < 10:
            print '*****************************************'
            print '*                                       *'
            print '*            ', 10-i, ' trials left             *'
            print '*                                       *'
            print '*****************************************'
            t.read_file()
            t.extract_words()
            t.user_input()
            t.backtrack()
            i = i + 1
            raw_input('Press enter to try again...')

