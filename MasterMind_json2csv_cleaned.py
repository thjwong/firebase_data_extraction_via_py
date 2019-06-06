import sys
import json
import csv
import re
#import argparse

from collections import Iterable
from collections import OrderedDict
from scipy.stats import entropy

# https://github.com/amirziai
def _construct_key(previous_key, separator, new_key):
    """
    Returns the new_key if no previous key exists, otherwise concatenates
    previous key, separator, and new_key
    :param previous_key:
    :param separator:
    :param new_key:
    :return: a string if previous_key exists and simply passes through the
    new_key otherwise
    """
    if previous_key:
        return u"{}{}{}".format(previous_key, separator, new_key)
    else:
        return new_key

   
    
def flatten(nested_dict, separator="_", root_keys_to_ignore=set()):
    """
    Flattens a dictionary with nested structure to a dictionary with no
    hierarchy
    Consider ignoring keys that you are not interested in to prevent
    unnecessary processing
    This is specially true for very deep objects

    :param nested_dict: dictionary we want to flatten
    :param separator: string to separate dictionary keys by
    :param root_keys_to_ignore: set of root keys to ignore from flattening
    :return: flattened dictionary
    """
    assert isinstance(nested_dict, dict), "flatten requires a dictionary input"
    assert isinstance(separator, six.string_types), "separator must be string"

    # This global dictionary stores the flattened keys and values and is
    # ultimately returned
    flattened_dict = dict()

    def _flatten(object_, key):
        """
        For dict, list and set objects_ calls itself on the elements and for
        other types assigns the object_ to
        the corresponding key in the global flattened_dict
        :param object_: object to flatten
        :param key: carries the concatenated key for the object_
        :return: None
        """
        # Empty object can't be iterated, take as is
        if not object_:
            flattened_dict[key] = object_
        # These object types support iteration
        elif isinstance(object_, dict):
            for object_key in object_:
                if not (not key and object_key in root_keys_to_ignore):
                    _flatten(object_[object_key], _construct_key(key,
                                                                 separator,
                                                                 object_key))
        elif isinstance(object_, list) or isinstance(object_, set):
            for index, item in enumerate(object_):
                _flatten(item, _construct_key(key, separator, index))
        # Anything left take as is
        else:
            flattened_dict[key] = object_

    _flatten(nested_dict, None)
    return flattened_dict

flatten_json = flatten






def main():
    arg1, arg2, arg3 = [0, None, False] #[None, False, []]
    if sys.argv[1:]:   # test if there is at least 1 argument
        #arg1 = sys.argv[1]
        arg1 = int(sys.argv[1])
        #print("argv1: ",arg1,"\n")
        if sys.argv[2:]:
            arg2 = sys.argv[2]
            arg3 = sys.argv[3]
            #print("argv2: ",arg2,"\n")
            #print("argv2: ",arg3,"\n")

    if arg1 == 0:
        print("JSON file converted to 1 game per row.\n")
    elif arg1 == 1:
        print("JSON file converted to 1 session per row.\n")
    
    if arg2 == None or not re.match("^[\w,\s-]+\.[A-Za-z]{3,4}$", arg2):
        #data = json.load(open('entropy-reasoning-export.json'))
        data = json.load(open('mastermind-studies-export.json'))
        print("default JSON input file name is used.\n")
    else:
        data = json.load(open(arg2))
        print("converting ", arg2)

    if arg3 == False or not re.match("^[\w,\s-]+\.[A-Za-z]{3}$", arg3):
        output_file = 'experiment-snapshot.csv'
        print("default csv output file name is used.\n")
    else:
        output_file = arg3
        print("exporting to ", arg3)
    
    data2file = open(output_file, 'w', newline='')
    csv_output = csv.writer(data2file, delimiter=",")

    omissionlist = ['numinjar', 'codelength']
    omissionindex = []

    relocationlist = ['truecode', 'guesses', 'feedback_neutral', 'aa_gamesuccess', 'gamesuccess']
    relocationindex = []

    foo = input("Your JSON file is being converted. [PRESS ANY KEY]\n")

    if arg1 == 0:
    ### 1 game per subject (transaction to database) per row    
        subjcnt = len(list(data.items()))
        print("subject count:", subjcnt)
        header_keys = []
        header_changed = 0
        indcj = -1 ## location of 'codejar'
        #indgs = -1 ## location of 'guesses'
        #indrt = -1 ## location of 'rt'
        elemcnt = -1
        for key, exptinstance in data.items():
            elemcnt = len(list(exptinstance.keys()))

            if list(exptinstance.keys()) == header_keys:
                header_changed = 0

            else:
                header_keys = list(exptinstance.keys())
                header_changed = 1
                print("Writing a new header row!")
                indcj = -1 ## Reset 'codejar' index
            ## the following needed instead of list(exptinstance.items())
            ## because Python 3.4 does not by default provide Dict.items in
            ## sorted ascending order
            #from collections import OrderedDict
            #OrderedDict(sorted(exptinstance.items()))
            #OrderedDict(sorted(exptinstance.items())).get('codejar')
            #list(OrderedDict(sorted(exptinstance.items())).keys())[0]
            #list(OrderedDict(sorted(exptinstance.items())).values())[0]
            gamecnt = len(exptinstance.get('truecode'))
            for i in range(0, elemcnt, 1):
                if(str(list(exptinstance.keys())[i])[0] == 'a'): ## header starts with an 'a'

                    if(str(list(exptinstance.keys())[i]).split("_")[1] in omissionlist):
                        omissionindex.append(i) ## skip & store their index for later process
                    elif(str(list(exptinstance.keys())[i]).split("_")[1] in relocationlist):
                        relocationindex.append(i) ## skip & store their index for later process
                    else:
                        if header_changed == 1:
                            data2file.write(str(list(exptinstance.keys())[i]).split("_")[1]+',')
                else:

                    if header_changed == 1: ## print changed header
                        if str(list(exptinstance.keys())[i]) in relocationlist:
                            relocationindex.append(i) ## skip & store the index
                        else:
                            data2file.write(str(list(exptinstance.keys())[i])+',')

                        if(str(list(exptinstance.keys())[i]) == 'codejar'): ## fields follow codejar
                            indcj = i

                            data2file.write('entropy'+',')
                            data2file.write('numguesses'+',')
                            #data2file.write('rtmean'+',')
                            data2file.write('rttotal'+',')
                            if (exptinstance.get('aa_gamesuccess') != None): 
                                data2file.write('gamesuccessproportion'+',')
                            ## fields relocated here:
                            data2file.write('truecode'+',')
                            data2file.write('guesses'+',')
                            
                        if(str(list(exptinstance.keys())[i]) == 'feedback_smiley'):
                            data2file.write('feedback_neutral'+',')

                        if(str(list(exptinstance.keys())[i]) == 'rt'):

                            if(exptinstance.get('aa_gamesuccess') != None):
                                data2file.write('gamesuccess'+',')


            ## store demographic entries
            nonlistvalues = []
            for i in range(0, elemcnt, 1):
                if not isinstance(list(exptinstance.values())[i], list):
                    if not (i in omissionindex): ## omit those in omission list
                        nonlistvalues.append(list(exptinstance.values())[i])
            if header_changed == 1:
                data2file.write('\r\n')
            for j in range(0, gamecnt, 1):
                for item in nonlistvalues:
                    data2file.write(str(item)+',')
                for i in range(0, elemcnt, 1):
                    if isinstance(list(exptinstance.values())[i], list): ## If they are list values


                        #if not (i in relocationindex):
                        if not (str(list(exptinstance.keys())[i]) in relocationlist):

                            data2file.write(str(list(exptinstance.values())[i][j]).replace(', ',';'))
                            #data2file.write(re.sub(r"\A\[(\d+)|(\d+)\]\Z|\A\[(\[)|(\])\]\Z", r"\1\2\3\4", str(list(exptinstance.values())[i][j]).replace(', ',';')))
                            data2file.write(',')

                        if(i == indcj): ## case of codejar


                            data2file.write(str(entropy(list(exptinstance.values())[i][j])/entropy([.5,.5])))
                            data2file.write(',')

                            if (exptinstance.get('aa_gamesuccess') != None):
                                if int(list(exptinstance.get('aa_gamesuccess'))[j][0]) == 0: ## Failed trial
                                    data2file.write(str(99))
                                    data2file.write(',')
                                else:
                                    data2file.write(str(len(list(exptinstance.get('guesses'))[j])))
                                    data2file.write(',')
                            #data2file.write(str(sum(map(int,list(exptinstance.values())[i][j]))/len(list(map(int,list(exptinstance.values())[i][j])))))
                            #data2file.write(',')
                            data2file.write(str(list(map(int,list(exptinstance.get('rt'))[j]))[-1])) ## RT Total (last item of elapsed time)
                            data2file.write(',')
                            if (exptinstance.get('aa_gamesuccess') != None):
                                #data2file.write(str(list(exptinstance.get('aa_gamesuccess'))[j]).replace(', ',';'))
                                gamesuccesstillnow = 0
                                for k in range(0, (j+1), 1):
                                    gamesuccesstillnow += int(list(exptinstance.get('aa_gamesuccess'))[k][0]) ## 1st & only item

                                gamesuccesstillnow = gamesuccesstillnow/gamecnt
                                data2file.write(str(gamesuccesstillnow))
                                data2file.write(',')
                            data2file.write(str(list(exptinstance.get('truecode'))[j]).replace(', ',';'))
                            data2file.write(',')
                            data2file.write(str(list(exptinstance.get('guesses'))[j]).replace(', ',';'))
                            data2file.write(',')

                        if (str(list(exptinstance.keys())[i]) == 'feedback_smiley'):
                            data2file.write(str(list(exptinstance.get('feedback_neutral'))[j]).replace(', ',';'))
                            data2file.write(',')

                        if (str(list(exptinstance.keys())[i]) == 'rt'):
                            if (exptinstance.get('aa_gamesuccess') != None): 
                                gstmp = exptinstance.get('aa_gamesuccess')
                                #print("aa_gamesucess: ", exptinstance.get('aa_gamesuccess'))



                                #print("aa_gamesucess class: ", gstmp)
                                data2file.write(str(list(exptinstance.get('aa_gamesuccess'))[j]).replace(', ',';'))
                                data2file.write(',')
                            
                data2file.write('\r\n')

            
    elif arg1 == 1:

        ### 1 subject (session / transaction to database) per row
        for key, exptinstance in data.items():
            csv_output.writerow([variable for variable, value in flatten(exptinstance).items()])
            csv_output.writerow([value for variable, value in flatten(exptinstance).items()])
    else:
        print("Invalid option. Please try again.")

    data2file.close()




    
    
if __name__== "__main__":
    main()

