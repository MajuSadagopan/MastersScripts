# Module Purpose: Create text-array of the most common words and word combinations
# Word grid is a 2d array of words and word combinations derived from all the sentences provided

#Import Libraries

import sys
sys.path.append('D:\ProgramFiles\Python27\winpython\WinPython-64bit-2.7.10.3\python-2.7.10.amd64\Lib\site-packages')


from operator import itemgetter
'''
#Global Variables
database = 'region_waterloo'
user = 'postgres'
password ='love2Learn'
host = 'localhost'
port = '5433'

#DB Variables
word_output_table = 'iht_word_combos4'
table_name = 'iht_trained_survey'
text_column = 'comment'
category = 'match_tabl'


#SQL QUERIES
tsvector_query="select gid, to_tsvector('simple',"+text_column+"),"+category+", "+text_column+" from "+table_name+" where "+category+" is not Null"
tstat_query="select array_agg(word) from ts_stat('"+"select to_tsvector(''simple'', "+text_column+") from "+table_name+"')"
'''


#WordGrid object, handles calls to db 
class wordgrid:

    def __init__(self,database,user,password,host,port):
        # Calls to connect to DB and create a cursor
        from operator import itemgetter
        import psycopg2 as psy
        self.conn = psy.connect(database=database,user=user,password=password,host=host,port=port)
        self.cur = self.conn.cursor()

        #Class variables to hold key terms & key stats
        self.key_terms = []
        self.key_stats = {}
        self.key_stats_array = []
        self.row_id = 0
        self.exclude = []
        self.word_id = 1
     
    def db_query(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()

    def return_key_terms(self):
        return list(set(self.key_terms))

    def exclude_terms(self, the_list):
        self.exclude += the_list

    def create_key_stats_array(self):
        keys = self.key_stats.keys()
        for key in keys:
            stats = self.key_stats[key]
            ndocs = len(set(stats['ndocs']))
            self.key_stats_array.append([key,stats['ncounts'],ndocs])
        
    def get_sorted_stats(self,statype):
        if len(self.key_stats_array) < 1:
            self.create_key_stats_array()
        
        if statype == 'c':
            return sorted(self.key_stats_array, key = itemgetter(1), reverse=True)
        else:
            return sorted(self.key_stats_array, key = itemgetter(2), reverse=True)
    
    # Creates statistics on words in the key words list, counts, no. docs etc.
    def update_keystats(self, word):
        if word in self.key_stats.keys():
            self.key_stats[word]['ncounts'] += 1
            self.key_stats[word]['ndocs'].append(self.row_id)
        else:
            self.key_stats[word] = {'ncounts':1,'ndocs':[self.row_id], 'id': self.word_id}
            self.word_id += 1

    # Insert keyword_stats into a dictionary
    def keywords2postgres(self, table_name):
        query = 'create table '+table_name+' (id integer, name varchar, ncounts integer, ndocs integer, w_length integer)'
        self.cur.execute(query)
        
        keys = self.key_stats.keys()
        for key in keys:
            query = "insert into "+table_name+' values('+str(self.key_stats[key]['id'])+", '"+str(key)+"', "+str(self.key_stats[key]['ncounts'])+', '+str(len(set(self.key_stats[key]['ndocs'])))+','+str(len(key.split()))+')'
            self.cur.execute(query)
            self.conn.commit()
        
            
    # Takes a dictionary and creates all the adjacent word combos
    def dict2combo(self,diction,length):
        keys = diction.keys()
        sent_combos = []
        for key in keys:
            if key+length < keys[-1]:
                word = diction[key]
                for num in range(1,length):
                    word = word+' '+diction[key+num]    

                word = word.replace("'","") 

                if word not in self.exclude:
                    self.update_keystats(word) 
                    if word not in sent_combos:
                        sent_combos.append(word)

        self.key_terms = self.key_terms + sent_combos
        return sent_combos

    
    # Takes dictionary and creates sentences and word grid
    def dict_sent(self,diction,combos):
        keys = diction.keys()
        sentence = ''
        group_array = []
        
        for key in keys:
            sentence = sentence + diction[key]+' '
            
        for num in range(1,combos+1):
                group_array = group_array + self.dict2combo(diction,num)
                
        return [sentence.replace("'",""),group_array]
    
   
    #Iterates over tsvector query, creates dictionary and uses helper functions to create stats
    def tsv_dict(self, tsv_group, index):  #Index refers to position of tsvector column
        tsv_return = []
        for row in tsv_group:
            self.row_id = int(row[0]) #Track current row
            sentence_dict = {}
            for pair in row[index].split():
                pair = pair.split(':')
                word = pair[0]
                number = pair[1]
                for num in number.split(','):
                    num = int(num)
                    sentence_dict[num] = word
            row = list(row)
            tsv_return.append([row[0],row[1],sentence_dict,self.dict_sent(sentence_dict,4)])
        return tsv_return

    
#Execution of Functions, vectors need to be created before db can be updated
'''
wg = wordgrid(database,user,password,host,port)
vectors = wg.db_query(tsvector_query)
vector_group = wg.tsv_dict(vectors,1)
wg.keywords2postgres(word_output_table)

combo_counts = wg.get_sorted_stats('d')

'''
