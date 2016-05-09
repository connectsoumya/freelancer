from Tkinter import Tk
from tkFileDialog import askopenfilename
import re
import random
import string
import numpy as np
import time
import operator
from copy import deepcopy
import logging
import logging.config
from flowtrack import Flowtrack

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
        self.latest_variable = {}
        self.line_no_old = np.inf
        self.mfile_line = None
        self.only_vars = None
        self.commands = None
        self.firstline = None
        self.updated_input = None
        logging.debug('Initialised Successfully.')

    def main(self):
        """
        The main function.
        :return:
        """
        self.read_file()
        self.first = True
        self.extract_words()
        # self.variable = 'resid'
        # self.line = 32

        self.steps = 14
        self.user_input()
        self.firstline = self.line
        self.present_inputs = {self.line : self.variable}
        print '=================================RESULTS================================='
        for i in xrange(1, self.steps+1):
            self.backtrack()
            # print '\n--------------------STEP ', i, ' COMPLETED---------------------------\n'


    def main_next(self):
        """

        :return:
        """
        # self.mfile = raw_input('This line is within a function. Which m-file calls this function? >>>')
        f = Flowtrack()
        self.mfile = f.main_method()
        self.mfile_line = int(raw_input('At which line does it call the function? >>>'))
        logging.debug('It calls the function at ' + str(self.mfile_line))
        self.firstline = deepcopy(self.mfile_line)
        # self.mfile_line = 6
        self.read_file_next()
        self.extract_words()
        self.line = deepcopy(int(self.mfile_line))
        self.present_inputs = {self.line : self.variable}
        for i in xrange(1, 10):
            self.backtrack()
            # print '\n--------------------STEP ', i, ' COMPLETED---------------------------\n'

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
        print filename
        line_no = 1
        self.dict_lines = {}
        for line in open(filename):
            lines = line.rstrip('\n')
            if re.search('\A((\s+\%)|(\%))', lines) is None:
                self.dict_lines[line_no] = lines
            line_no += 1
        self.commands = []
        for line in open('command.txt'):
            lines = line.rstrip('\n')
            self.commands.append(lines)
        logging.debug('Read file successfully.')

    def read_file_next(self):
        """
        This method is for the gui to select and read the file.
        :return:
        """
        filename = self.mfile
        line_no = 1
        self.dict_lines = {}
        for line in open(filename):
            lines = line.rstrip('\n')
            if re.search('\A((\s+\%)|(\%))', lines) is None:
                self.dict_lines[line_no] = lines
            line_no += 1
        self.commands = []
        for line in open('command.txt'):
            lines = line.rstrip('\n')
            self.commands.append(lines)
        logging.debug('Read file successfully.')

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
        logging.debug('Extracted words successfully.')

    def user_input(self):
        """
        This method takes the input from the user.
        :return:
        """
        self.variable = raw_input('Please enter the variable name >>>')
        logging.debug(self.variable)
        line = raw_input('Please enter the line number >>>')
        self.firstline = line
        self.line = int(line)
        logging.debug(self.line)
        # steps = raw_input('Please enter the number of steps >>>')
        # self.steps = int(steps)
        self.present_inputs = {self.line : self.variable}
        # self.mfile = raw_input('This line is within a function. Which m-file calls this function? >>>')
        # self.mfile_line = raw_input('At which line does it call the function? >>>')

    def extract_variables_only(self):
        """
        This method extracts only the variables present in line self.line.
        :return: Saves a list of variables. (Returns none)
        """
        if self.first:
            try:
                _list = self.dict_variables[self.line]
            except KeyError:
                print 'Line number out of range.'
                logging.error('Line number out of range.')
            try:
                idx = _list.index(self.variable)
            except:
                print self.variable, ' does not exist in line ', self.line
                logging.error('Variable does not exist.')
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
        print '..................................................'
        logging.debug('Extracted variables only.')


    def get_updated_input(self):
        if self.first:
            self.extract_variables_only()
        present_variable = deepcopy(self.only_vars)
        self.updated_input = {}
        for var in self.only_vars:
            if var == self.variable:
                present_variable.remove(var)
        logging.debug(present_variable)
        for var in present_variable:
            for line_no in reversed(range(1, self.line)):
                try:
                    prev_line = self.dict_variables[line_no]  # prev_line is a list
                    prev_line = self.varonly(prev_line)
                    # print prev_line

                    # logging.debug(prev_line)
                    if prev_line[0] == var:
                        print 'Variable ', var, ' in line ', line_no
                        var_tmp = deepcopy(var)
                        if self.line_no_old > line_no:
                            self.latest_variable[var_tmp] = line_no
                        elif self.line_no_old == line_no:
                            self.latest_variable[var_tmp] = line_no
                        self.updated_input[line_no] = var
                        self.line_no_old = deepcopy(line_no)
                        break
                    elif self.dict_variables[line_no][0] == 'function':
                        for fn_arg in prev_line:
                            if fn_arg == var:
                                print 'Variable ', var, ' in line ', line_no
                                var_tmp = deepcopy(var)
                                if self.line_no_old > line_no:
                                    self.latest_variable[var_tmp] = line_no
                                elif self.line_no_old == line_no:
                                    self.latest_variable[var_tmp] = line_no
                                self.updated_input[line_no] = var
                                self.line_no_old = deepcopy(line_no)
                                break
                except:
                    # print 'Probably something went wrong.'
                    continue
            # if not caught:
            #     if self.infunction():
            #         self.mfile = raw_input('This line is within a function. Which m-file calls this function? >>>')
            #         self.mfile_line = raw_input('At which line does it call the function? >>>')
        logging.debug('All updated inputs extracted.')

    def backtrack(self):
        """
        This method backtracks as requested by the user.
        :return:
        """
        for self.line, self.variable in self.present_inputs.iteritems():
            self.get_updated_input()
            logging.debug('Backtracked.')
        self.present_inputs = deepcopy(self.updated_input)

#----------------------------------------------------------------------------------------------------------------------#

    def infunction(self):
        """
        This method checks if the line number self.line is within a function.
        :param var: The variable.
        :return: Bool (True/False)
        """
        varinfunc = False
        for i in xrange(1, self.firstline):
            for word in self.dict_variables[i]:
                if word == 'function':
                    varinfunc = True
                    # self.mfile = raw_input('This line is within a function. Which m-file calls this function? >>>')
                    # mfile_line = raw_input('At which line does it call the function? >>>')
                    # self.mfile_line = int(mfile_line)
                    break
            if varinfunc:
                break
        return varinfunc

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

    def varonly(self, _list):
        """
        Extracts just the variables from _list.
        :param _list: A list.
        :return:
        """
        only_vars = []
        for var in _list:
            var_idx = _list.index(var)
            try:
                next_char = _list[var_idx + 1]
                if next_char[0] == '(':
                    if re.match('([a-z]+)', var) is not None:
                        for command in self.commands:
                            if command == var:
                                pass
                    else:
                        if any(c.isalpha() for c in var):
                            only_vars.append(var)
                elif next_char[0] == ' ' and next_char[1] == '(':
                    if re.match('([a-z]+)', var) is not None:
                        for command in self.commands:
                            if command == var:
                                pass
                    else:
                        if any(c.isalpha() for c in var):
                            only_vars.append(var)
                else:
                    if any(c.isalpha() for c in var):
                        only_vars.append(var)
            except IndexError:
                continue
        return only_vars

    # def varonly(self, _list):
    #     """
    #     Extracts just the variables from _list.
    #     :param _list: A list.
    #     :return:
    #     """
    #     only_vars = deepcopy(_list)
    #     for var in _list:
    #         for command in self.commands:
    #             if var == command:
    #                 only_vars.remove(var)
    #         if not any(c.isalpha() for c in var):
    #             only_vars.remove(var)
    #     # print only_vars
    #     return only_vars

# if __name__ == '__main__':
#     t = Tracker()
#     if time.time() < 1462159992:
#         t.main()
#     else:
#         print 'File expired. Follow the instructions below:'
#         t.passcode()
#         i = 0
#         while i < 10:
#             print '*****************************************'
#             print '*                                       *'
#             print '*            ', 10-i, ' trials left             *'
#             print '*                                       *'
#             print '*****************************************'
#             t.read_file()
#             t.extract_words()
#             t.user_input()
#             t.backtrack()
#             i = i + 1
#             raw_input('Press enter to try again...')

if __name__ == '__main__':
    t = Tracker()
    if time.time() < 1462779908:
        t.main()
        if t.infunction():
            while True:
                latest_variable = []
                v_temp = deepcopy(t.latest_variable)
                sorted_v = sorted(v_temp.items(), key=operator.itemgetter(1))
                # print v_temp
                v_old = np.inf
                for i in sorted_v:
                    if i[1] <= v_old:
                        latest_variable.append(i[0])
                        v_old = i[1]
                    else:
                        break
                print latest_variable
                t = Tracker()
                for i in xrange(0,1):#latest_variable:
                    try:
                        t.variable = '______'
                        t.first = False
                        t.only_vars = latest_variable
                        t.main_next()
                    except TypeError:
                        continue
                a = raw_input('Continue backtracking? [y/n]')
                if a != 'y':
                    break
        print '========================================================================'
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
            t.main()
            if t.infunction():
                while True:
                    latest_variable = []
                    v_temp = deepcopy(t.latest_variable)
                    sorted_v = sorted(v_temp.items(), key=operator.itemgetter(1))
                    # print v_temp
                    v_old = np.inf
                    for i in sorted_v:
                        if i[1] <= v_old:
                            latest_variable.append(i[0])
                            v_old = i[1]
                        else:
                            break
                    print latest_variable
                    t = Tracker()
                    for i in xrange(0,1):#latest_variable:
                        try:
                            t.variable = '______'
                            t.first = False
                            t.only_vars = latest_variable
                            t.main_next()
                        except TypeError:
                            continue
                    a = raw_input('Continue backtracking? [y/n]')
                    if a != 'y':
                        break
            print '========================================================================'