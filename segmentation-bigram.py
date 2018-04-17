import re
import sys

sys.setrecursionlimit(1000000)
name = "corpus_for_ass2train.txt" #训练集
name1 = "corpus_for_ass2test.txt" #测试集
name2 = "result.txt"  #将测试集结果输出
maxlength = 6 #假设最长词语的长度
ori_dict = {}  #存储测试集中bigram信息的二元字典


#读入训练集
def load(name):
    # 在文件中读取数据
    with open(name, "r") as f:
        sentence_ori = f.read()
    return sentence_ori


# 分词并统计词频
def segmentation(lists, dicts=None):
    # 建立二元字典，创建无向图
    if dicts != None:
        for i in range(len(lists) - 1):
            if lists[i] not in dicts:
                dicts.update({lists[i]: {'num': 1, lists[i + 1]: 1}})
            else:
                dicts[lists[i]]['num'] += 1
                if lists[i + 1] not in dicts[lists[i]]:
                    dicts[lists[i]].update({lists[i + 1]: 1})
                else:
                    dicts[lists[i]][lists[i + 1]] += 1
    return lists

#导入测试集
def load_test(name1):
    # 在文件中读取数据
    sentence_ori = []
    for line in open(name1, "r"):
        sentence_ori.append(line[:-1])
    return sentence_ori

# 将句子分词并记录分词结果
def segment_sentence_fir(sen):
    allpath = []
    path = []
    # print(sen)
    num = 0
    #正向切分找到所有切分结果
    segment_sentence_forward(sen=sen, allpath=allpath, lastword=sen,
                             lastpath=path)
    path = []
    #如果正向切分没有将所有结果切分出来，则进行反向切分
    if len(allpath)>=500000:
        segment_sentence_backward(sen, path, allpath)
    # print(allpath)
    return allpath

# 向前递归记录分词结果
def segment_sentence_forward(sen, lastpath, allpath, lastword):
    path = lastpath[0:len(lastpath)]
    num = 0
    #从句子开始长度为最大词语长度范围内的词
    for length in range(maxlength):
        if ( sen[:maxlength-length] in ori_dict.keys() or( maxlength-length == 1 and num==0))and (maxlength - length) <= len(sen) and len(allpath)<= 500000:
            num = num + 1
            if num > 1:
                path = path[:-1]
            path.append(sen[:maxlength-length])
            #print(path)
            #找到当前词后，将当前词切割出来，继续寻找剩下句子的切割方法
            nextnum = segment_sentence_forward(sen[maxlength-length:], path, allpath, sen[:maxlength-length])
            #如果句子结束，则将所找到的路径存入该句子总路径集
            if maxlength-length == len(sen):
                #print(path)
                allpath.append(path)
    return num

# 向后递归分词结果
def segment_sentence_backward(sen, lastpath, allpath):
    path = lastpath[0:len(lastpath)]
    num = 0
    if len(sen)==0:
        return 0
    for length in range(maxlength):
        if (sen[length-maxlength:] in ori_dict.keys() or (maxlength - length == 1 and num == 0)) and (
            maxlength - length) <= len(sen) and len(allpath) <= 600000:
            num = num + 1
            if num > 1:
                path = path[:-1]
            path.append(sen[length - maxlength:])
            # 找到当前词后，将当前词切割出来，继续寻找剩下句子的切割方法
            nextnum = segment_sentence_backward(sen[:length - maxlength], path, allpath)
            if maxlength-length == len(sen):
                path1 = path
                path1.reverse()
                allpath.append(path1)
    return num


#找到一段文章的分词结果
def segment1(sen):
    #将得到的文本用标点符号分隔开
    phrase_ori = re.split("(，|（|）|《|》|、|；|。|！|？|·|“|”|：)", sen)
    #print(phrase_ori)
    psegment = []
    best_path = []
    for phrase in phrase_ori:
        psegment.append(segment_sentence_fir(phrase))
    for psegment_temp in psegment:
        #print(len(psegment_temp))
        best_path = best_path + get_best_path(psegment_temp)[0]
    return best_path




# 得到一句话的最优路径
def get_best_path(allpath):
    maxpro = 0
    bestpath = []
    for i in range(len(allpath)):
        temppro = calculate_word_path_probability(allpath[0-i])
        if maxpro < temppro:
            maxpro = temppro
            bestpath = allpath[0-i]
    #print(bestpath, maxpro)
    return bestpath, maxpro


# 2-gram计算单个路径的可能性
def calculate_word_path_probability(path):
    if path[0] in ori_dict.keys():
        probability = float(ori_dict[path[0]]['num'] + 1)
    else:
        probability = 1.0000000
    for i in range(1, len(path)):
        if path[i - 1] in ori_dict.keys():
            # print(ori_dict[path[i-1]])
            if path[i] in ori_dict[path[i - 1]].keys():
                probability = probability * (ori_dict[path[i - 1]][path[i]] + 1) / (ori_dict[path[i - 1]]['num'] + 0.5*len(ori_dict.keys()))
            else:
                probability = 0.5*probability / (ori_dict[path[i - 1]]['num'] + 0.5*len(ori_dict.keys()))
        else:
            probability =  probability / 1.5*len(ori_dict.keys())
    #print(probability)
    return probability


#得到所有句子的最佳路径
def all_bestpath(sens):
    allbestpath = []
    for sen in sens:
        allbestpath.append(segment1(sen))
    return allbestpath

#将得到的结果规范化后写入文件
def put_in_txt(name2,all_path):
    with open(name2, 'w') as f:
        for i in all_path:
            i = str(i).strip('[').strip(']').replace(","," ").replace("\'","")
            f.write(i+"\n")


if __name__ == '__main__':
    # 设置词库
    ori_wordbase = load(name).split()
    wordbase = list(set(ori_wordbase))
    # print(wordbase)

    # 设置储存gram信息的字典
    segmentation(ori_wordbase, ori_dict)
    # print(ori_dict)

    # 分割句子
    sentences = load_test(name1)


    #分割并找出最优路径
    allpath = all_bestpath(sentences)

    #写入文件
    put_in_txt(name2,allpath)