## Muhan Yuan
## python WSD.py <word>.wsd
## Word sense disambiguation using Naive Bayes

import sys
from bs4 import BeautifulSoup
import string
import json
import random

def sentence_to_features(s,target):
    s = ''.join(ch for ch in s if ch not in set(string.punctuation))
    res = list(set([i.lower() for i in s.strip().split(" ") if i !="" and i!= target]))
    return res

def P_calculate(dic, name, smooth = False, smooth_list = []):
    sum_value = 0
    if smooth == False:
        return dic[name]/float(sum(dic.values()))
    else:
        if name in dic:
            return (dic[name]+1)/(float(sum(dic.values()))+len(smooth_list))
        else:
            return 1/(float(sum(dic.values()))+len(smooth_list))

def n_fold(data, n, k):
    train = [v for i,v in enumerate(data) if i % 5 != k]
    test = [v for i,v in enumerate(data) if i % 5 == k]
    return train, test


def max_index(l):
    max_value = max(l)
    max_index = l.index(max_value)
    return max_index

def main():
    random.seed(42)

    with open(sys.argv[1],"rb") as datafile:
        soup = BeautifulSoup(datafile,"lxml")

    ins_list = soup.find_all('instance')
    data_frame = [[ins.find("answer").get("instance") , ins.find("answer").get("senseid").split("%")[1] , ins.find("context").string] for ins in ins_list]
    target_word = ins_list[0].find("answer").get("senseid").split("%")[0]
    data_frame = random.sample(data_frame, len(data_frame))

    file_out = open(sys.argv[1].split(".")[0]+".wsd.out","w")
    res = []

    # Using the dataset to do a 5-fold cross valiadation, and output the testing accuracy for each fold
    for i in range(5):
        file_out.write("Fold "+str(i+1)+"\n")
        training, testing = n_fold(data_frame,5,i)
        training_frame = [[ins[0],ins[1], sentence_to_features(ins[2],target_word)] for ins in training]
        testing_frame = [[ins[0],ins[1], sentence_to_features(ins[2],target_word)] for ins in testing]

        sense_dic = {}
        sense_word_dic = {}
        word_list = []

        for ins in training_frame:
            if ins[1] not in sense_dic:
                sense_dic[ins[1]] = 1
            else:
                sense_dic[ins[1]] += 1

            if ins[1] not in sense_word_dic:
                sense_word_dic[ins[1]] = {}

            for feature in ins[2]:
                if feature not in sense_word_dic[ins[1]]:
                    sense_word_dic[ins[1]][feature] = 1
                else:
                    sense_word_dic[ins[1]][feature]+= 1

        for ins in training_frame + testing_frame:
            for feature in ins[2]:
                if feature not in word_list:
                    word_list.append(feature)

        correct = 0
        ini_temp_sense_list = []
        for sense in sense_dic:
            ini_temp_sense_list.append(P_calculate(sense_dic,sense))

        for ins in testing_frame:
            temp_sense_list = list(ini_temp_sense_list)

            for feature in ins[2]:
                for sense_num in range(len(temp_sense_list)):

                    temp_sense_list[sense_num] = float(temp_sense_list[sense_num])* P_calculate(sense_word_dic[sense_dic.keys()[sense_num]], feature, True, word_list)

            file_out.write(ins[0]+" "+target_word+"%"+str(ins[1])+"\n")
            if ins[1] == sense_dic.keys()[max_index(temp_sense_list)]:
                correct+= 1

        res.append(float(correct)/len(testing_frame))
        print "Fold "+str(i+1)+": "+str(float(correct)/len(testing_frame))
    print "Overall Accuracy {0}".format( sum(res)/len(res))

main()
