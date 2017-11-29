import sys
from bs4 import BeautifulSoup
import string
import json
import random

random.seed(22)

# class word_instance():
def sentence_to_features(s,target):
    s = ''.join(ch for ch in s if ch not in set(string.punctuation))
    res = list(set([i.lower() for i in s.strip().split(" ") if i !="" and i!= target]))
    return res

def P_calculate(dic, name, smooth = False, smooth_list = []):
    sum = 0
    if smooth == False:
        for n in dic:
            sum += dic[n]
        return dic[name]/float(sum)
    else:
        for n in dic:
            sum += dic[n]
        if name in dic:
            return (dic[name]+1)/(float(sum)+len(smooth_list))
        else:
            return 1/(float(sum)+len(smooth_list))

def n_fold(data, n, k):
    unit = len(data)/n + 1
    train = []
    test = []
    count = 0
    for x in range(n):
        if x==k:
            for y in range(unit):
                try:
                    test.append(data[count])
                    count+= 1
                except:
                    break
        else:
            for y in range(unit):
                try:
                    train.append(data[count])
                    count+= 1
                except:
                    break

    return train, test


def max_index(l):
    max_value = max(l)
    max_index = l.index(max_value)
    return max_index
# python WSD.py <word>.wsd
with open(sys.argv[1],"rb") as datafile:
    soup = BeautifulSoup(datafile,"lxml")
    ins_list = soup.find_all('instance')
    data_frame = [[ins.find("answer").get("instance") , ins.find("answer").get("senseid").split("%")[1] , ins.find("context").string] for ins in ins_list]
    target_word = ins_list[0].find("answer").get("senseid").split("%")[0]
    data_frame = random.sample(data_frame, len(data_frame))

    file_out = open(sys.argv[1].split(".")[0]+".wsd.out","w")
    res = []
    for i in range(5):
        file_out.write("Fold "+str(i+1)+"\n")
        training, testing = n_fold(data_frame,5,i)
        # print len(training),len(testing)
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
        # print json.dumps(sense_word_dic)
        for ins in training_frame:
            for feature in ins[2]:
                if feature not in word_list:
                    word_list.append(feature)

        for ins in testing_frame:
            for feature in ins[2]:
                if feature not in word_list:
                    word_list.append(feature)
        # print len(word_list)
        correct = 0
        ini_temp_sense_list = []
        for sense in sense_dic:
            ini_temp_sense_list.append(P_calculate(sense_dic,sense))
        # print testing_frame[0]
        for ins in testing_frame:
            temp_sense_list = list(ini_temp_sense_list)

            for feature in ins[2]:
                for sense_num in range(len(temp_sense_list)):
                    # print sense_num
                    temp_sense_list[sense_num] = float(temp_sense_list[sense_num])* P_calculate(sense_word_dic[sense_dic.keys()[sense_num]], feature, True, word_list)
                    # print sense_dic.keys()[sense_num]
            # print sense_dic.keys()[max_index(temp_sense_list)]
            # print temp_sense_list
            file_out.write(ins[0]+" "+target_word+"%"+str(ins[1])+"\n")
            if ins[1] == sense_dic.keys()[max_index(temp_sense_list)]:
                correct+= 1
            # else:
            #     print sense_dic.keys()[max_index(temp_sense_list)]
            #     print ins
        res.append(float(correct)/len(testing_frame))
        print "Fold "+str(i+1)+": "+str(float(correct)/len(testing_frame))
    print sum(res)/len(res)
