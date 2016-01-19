import sys
import psycopg2 as psy
import numpy
from sklearn import metrics

sys.path.append('D:\ProgramFiles\Python27\winpython\WinPython-64bit-2.7.10.3\python-2.7.10.amd64\Lib\site-packages')

conn = psy.connect(database='region_waterloo', user='postgres', password='love2Learn', host='localhost',port='5433')
cur= conn.cursor()

#=== Database query variables ======
table_name='iht_trained_survey'
text_column='comment'
category='match_tabl'

#=== Database queries ================
table_query="select gid, to_tsvector('simple',"+text_column+"),"+category+", "+text_column+" from "+table_name+" where "+category+" is not Null"
cur.execute(table_query)
tsvectors = cur.fetchall()

tstat_query="select * from ts_stat('"+"select to_tsvector(''simple'', "+text_column+") from "+table_name+"')"
cur.execute(tstat_query)
tstats = cur.fetchall()

tstat_query="select * from ts_stat('"+"select to_tsvector(''simple'',"+text_column+') from '+table_name+"') where ndoc>5 and nentry <170"
cur.execute(tstat_query)
keys = cur.fetchall()

match_tables = "select distinct("+category+") from "+table_name+" where "+category+" is not Null"
cur.execute(match_tables)
categories=cur.fetchall()


#=== Data Manipulation Functions =======
def to_list(tuple_list,pos):
    word_list=[]
    for tup in tuple_list:
        word_list.append(tup[pos])
    return word_list

    

def serialize(word_list):
    forward_key={}
    reverse_key={}
    for i in range(len(word_list)):
        forward_key[word_list[i]]= i
        reverse_key[i] = word_list[i]
    return [forward_key, reverse_key]





def ml_convert(word_key,category_key,keywords):
    keys=keywords[1].keys()
    big_array=[]
    for vector in tsvectors:
        med_array=[]
        small_array=[]
        vector_dict = {}
        for word in vector[1].split():
            key_q = word.split(':')[0]
            key = key_q[1:len(key_q)-1]
            small_array.append(word_key[0][key])

        small_array=grid(small_array,keys)
        med_array=[vector[0],small_array,category_key[0][vector[2]],vector[3]]
        big_array.append(med_array)
    return big_array



def ml_prep(word_key,category_key,keywords):
    keys=keywords[1].keys()
    big_array=[]
    for vector in tsvectors:
        med_array=[]
        small_array=[]
        vector_dict = {}
        for word in vector[1].split():
            key_q = word.split(':')[0]
            key = key_q[1:len(key_q)-1]
            small_array.append(word_key[0][key])
            
            str_num = word.split(':')[1]

            for num in str_num.split(','):
                place = int(num)
                vector_dict[place] = key


        med_array=[vector[0],small_array,category_key[0][vector[2]],vector[3],vector_dict]
        big_array.append(med_array)
    return big_array


def grid(text, words_dict):
    key_list = words_dict[0].keys()
    sm = []
    for key in key_list:
        if key in text:
            if type(key)== str:
                sm.append(words_dict[0][key])
            else:
                sm.append(key)
        else:
            sm.append(0)
            
    return sm


def dic2list(dic, words_dict):
    keys = dic.keys()
    dlist = []
    for key in keys:
	    dlist.append(words_dict[dic[key]])
    return dlist


def set_of(text,length):
    group = []
    for num in range(len(text)-(length-1)):
	    a= str(text[num])
	    for i in range(1,length):
		    a=a+'.'+str(text[num+i])
	    group.append(a)
    return set(group)


def ml_input(ml_prepar, words_dict,num):
  
    output =[]
    for row in ml_prepar:
        vector_dict = row[4]
        vector_list = dic2list(vector_dict, words_dict[0])
        vector_sets = set_of(vector_list,num)
        small_array = row[1] + list(vector_sets)
        output.append([row[0],small_array,row[2],row[3],row[4]])

        for code in vector_sets:
            wcode = int(code.replace('.',''))
            words_dict[0][code] = wcode
            words_dict[1][wcode] = code

    return [output,words_dict]


def ml_grid_data(ml_input,words_dict):
    output =[]
    for row in ml_input:
        grid_row = grid(row[1],words_dict)
        output.append([row[0],grid_row,row[2],row[3],row[4]])
    return output


category_dict = serialize(to_list(categories,0))
words_dict= serialize(to_list(tstats,0))
keywords= serialize(to_list(keys,0))
ml_prepar = ml_prep(words_dict,category_dict,keywords)
ml_grid_input = ml_input(ml_prepar, words_dict,2)

words_dict = ml_grid_input[1]
ml_grid = ml_grid_input[0]
ml_trainer_set = ml_grid_data(ml_grid, words_dict)

vectors_list = numpy.array(to_list(ml_trainer_set,1))
categories_list = numpy.array(to_list(ml_trainer_set,2))

print len(vectors_list[0])

from sklearn import svm
clf = svm.SVC(gamma=0.001, C=100.)
clf.fit(vectors_list[:100], categories_list[:100])

def model_accuracy(model,target,tru_val, indx):
    correct = 0
    error = 0
    for num in range(indx, len(target)):
        if int(model.predict(target[num])) == tru_val[num][2]:
            correct += 1
        else:
            error += 1
    return float(correct)/(float(correct)+float(error))

#print category_dict[1][ml_trainer_set[101][2]]
#print category_dict[1][int(clf.predict(vectors_list[101]))]

print model_accuracy(clf,vectors_list,ml_trainer_set,100)



                    
            

            
        
