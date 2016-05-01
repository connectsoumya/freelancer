import re
import os
from fnmatch import fnmatch

class Flowtrack(object):
    def __init__(self):
        pass

    def checkVariables(self,name):
        namefile = self.mylistwithpath[self.mylist.index(name)]
        fileII = open(namefile, 'r')
        variables = ''
        keywords = ['if','for','while','function']
        for lineII in fileII:
            for keyword in keywords:
                if keyword in lineII:
                    lineII = ''
            if lineII.find('%') != -1:
                lineII = lineII[0:lineII.index('%')]
            if lineII.find('=') != -1:
                lineII = lineII[0:lineII.index('=')]
                variables = variables + '\t' + lineII
        return variables

    @staticmethod
    def findWholeWord(w):
        return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

    @staticmethod
    def findComment(w):
        return re.compile(r'\'.*({0}).*\''.format(w), flags=re.IGNORECASE).search

    @staticmethod
    def insensitiveReplace(word, replace, line):
        insensitive = re.compile(re.escape(word), re.IGNORECASE)
        return insensitive.sub(replace, line)

    def checkFunctions(self, name):
        namefileI = self.mylistwithpath[self.mylist.index(name)]
        fileI = open(namefileI, 'r')
        for indexI, lineI in enumerate(fileI):
            self.indentation = self.indentation + ' '
            #remove comments
            if lineI.find('%') != -1:
                lineI = lineI[0:lineI.index('%')]
            #remove function declarations
            if lineI.find('function') != -1:
                lineI = ''
            #check text function names
            for funcI in self.mylist:
                if "'"+funcI+"'" in lineI:
                    lineI = lineI.replace("'"+funcI+"'", "")
                if '"'+funcI+'"' in lineI:
                    lineI = lineI.replace('"'+funcI+'"', "")
                if bool(self.findComment(funcI)(lineI)):
                    lineI = self.insensitiveReplace(funcI, '', lineI)
            if (bool(self.findWholeWord(name)(lineI)) or bool(self.findComment(name)(lineI))):
                lineI = self.insensitiveReplace(name, '', lineI)
            #check for other functions in line
            for funcI in self.mylist:
                if bool(self.findWholeWord(funcI)(lineI)):
                    #check for variables getting updated in func
                    variablesI = self.checkVariables(funcI)
                    self.result.write(self.indentation+namefileI+'\t'+str(indexI)+'\t'+funcI+'\t'+variablesI+'\n')
                    self.checkFunctions(funcI)
            self.indentation = self.indentation[:-1]

    # get a list of all .m files
    def main_method(self):
        # start = raw_input("Please enter starting file name:")
        # ignore = raw_input("Please enter a folder you want to ignore (if any):")
        start = raw_input("This line is within a function. Which m-file calls this function?"
                          "If the name of the file is 'example.m', write 'example' >>>")
        ignore = ''

        #get the m files
        root = 'folders/'
        pattern = "*.m"
        self.mylist = []
        self.mylistwithpath = []
        self.indentation = ''
        ignorepattern = ignore+"\\*.m"

        for path, subdirs, files in os.walk(root):
            for name in files:
                if fnmatch(os.path.join(path, name), ignorepattern):
                    print(os.path.join(path, name), ignorepattern)
                elif fnmatch(name, pattern):
                    self.mylist.append(name[:-2])
                    self.mylistwithpath.append(os.path.join(path, name))

        #open the file where we should start
        startfile = self.mylistwithpath[self.mylist.index(start)]
        file = open(startfile, 'r')
        #create the results file
        result = open(start+'-result.txt','w')
        result.write('file\tline\tcalls\tvariables modified\n')

        #read the file line by line and check for *.m files, functions, variables
        for index, line in enumerate(file):
            #remove comments
            if line.find('%') != -1:
                line = line[0:line.index('%')]
            #remove function declarations
            if line.find('function') != -1:
                line = ''
            #check text function names
            for func in self.mylist:
                if "'"+func+"'" in line:
                    line = line.replace("'"+func+"'", "")
                if '"'+func+'"' in line:
                    line = line.replace('"'+func+'"', "")
                if bool(self.findComment(func)(line)):
                    line = self.insensitiveReplace(func, '', line)
            if (bool(self.findWholeWord(start)(line)) or bool(self.findComment(start)(line))):
                line = self.insensitiveReplace(start, '', line)
            #check for other functions in line
            for func in self.mylist:
                if bool(self.findWholeWord(func)(line)):
                    #check for variables getting updated in func
                    variables = self.checkVariables(func)
                    result.write(startfile+'\t'+str(index)+'\t'+func+'\t'+variables+'\n')
                    self.checkFunctions(func)
        return startfile

if __name__ == '__main__':
    f = Flowtrack()
    f.main_method()