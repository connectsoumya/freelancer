#define checkvariables
def checkVariables(name):
    namefile = mylistwithpath[mylist.index(name)]
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

import re

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def findComment(w):
    return re.compile(r'\'.*({0}).*\''.format(w), flags=re.IGNORECASE).search

def insensitiveReplace(word, replace, line):
    insensitive = re.compile(re.escape(word), re.IGNORECASE)
    return insensitive.sub(replace, line)

def checkFunctions(name):
    namefileI = mylistwithpath[mylist.index(name)]
    fileI = open(namefileI, 'r')
    for indexI, lineI in enumerate(fileI):
        global indentation
        indentation = indentation + ' '
        #remove comments
        if lineI.find('%') != -1:
            lineI = lineI[0:lineI.index('%')]
        #remove function declarations
        if lineI.find('function') != -1:
            lineI = ''
        #check text function names
        for funcI in mylist:
            if "'"+funcI+"'" in lineI:
                lineI = lineI.replace("'"+funcI+"'", "")
            if '"'+funcI+'"' in lineI:
                lineI = lineI.replace('"'+funcI+'"', "")
            if bool(findComment(funcI)(lineI)):
                lineI = insensitiveReplace(funcI, '', lineI)
        if (bool(findWholeWord(name)(lineI)) or bool(findComment(name)(lineI))):
            lineI = insensitiveReplace(name, '', lineI)
        #check for other functions in line
        for funcI in mylist:
            if bool(findWholeWord(funcI)(lineI)):
                #check for variables getting updated in func
                variablesI = checkVariables(funcI)
                result.write(indentation+namefileI+'\t'+str(indexI)+'\t'+funcI+'\t'+variablesI+'\n')
                checkFunctions(funcI)
        indentation = indentation[:-1]

# get a list of all .m files
import os
from fnmatch import fnmatch

start = raw_input("Please enter starting file name:")
ignore = raw_input("Please enter a folder you want to ignore (if any):")

#get the m files
root = 'folders/'
pattern = "*.m"
mylist = []
mylistwithpath = []
indentation = ''
ignorepattern = ignore+"\\*.m"

for path, subdirs, files in os.walk(root):
    for name in files:
        if fnmatch(os.path.join(path, name), ignorepattern):
            print(os.path.join(path, name), ignorepattern)
        elif fnmatch(name, pattern):
            mylist.append(name[:-2])
            mylistwithpath.append(os.path.join(path, name))

#open the file where we should start
startfile = mylistwithpath[mylist.index(start)]
print startfile
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
    for func in mylist:
        if "'"+func+"'" in line:
            line = line.replace("'"+func+"'", "")
        if '"'+func+'"' in line:
            line = line.replace('"'+func+'"', "")
        if bool(findComment(func)(line)):
            line = insensitiveReplace(func, '', line)
    if (bool(findWholeWord(start)(line)) or bool(findComment(start)(line))):
        line = insensitiveReplace(start, '', line)
    #check for other functions in line
    for func in mylist:
        if bool(findWholeWord(func)(line)):
            #check for variables getting updated in func
            variables = checkVariables(func)
            result.write(startfile+'\t'+str(index)+'\t'+func+'\t'+variables+'\n')
            checkFunctions(func)