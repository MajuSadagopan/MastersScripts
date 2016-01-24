import sklearn
import numpy


#Global Variables
database = 'region_waterloo'
user = 'postgres'
password ='love2Learn'
host = 'localhost'
port = '5433'


#SQL QUERIES
#tsvector_query="select gid, to_tsvector('simple',"+text_column+"),"+category+", "+text_column+" from "+table_name+" where "+category+" is not Null"
#tstat_query="select array_agg(word) from ts_stat('"+"select to_tsvector(''simple'', "+text_column+") from "+table_name+"')"


#DB Variables
keys_table = 'iht_word_combos'
keys_table2 = 'iht_word_combos2'
key_col = 'name'
key_id = 'id'

table_name = 'iht_trained_survey'
text_column = 'comment'
category = 'match_tabl'


class sk_sql:
    def __init__(self,database,user,password,host,port):
        # Calls to connect to DB and create a cursor
        import word_grid as wg
        import nltk
        
        self.wgrid = wg.wordgrid(database,user,password,host,port)
        self.key_dict = {}
        self.sk_inputs = {}

    # Turns two column query to a dictionary
    def query_dict(self,q_results):
        result_list = {}
        for row in q_results:
            result_list[row[0]] = row[1]
        return result_list
    
    def set_keydict(self,table_name, text_column, id_col):
        query = "select " + text_column + ", "+id_col+" from "+table_name+" where ndocs > 20"
        results = self.wgrid.db_query(query)
        key_dict = self.query_dict(results)
        self.key_dict = key_dict

    def list2dict(self, wlist):
        wdict = {}
        wset = list(set(wlist))
        for num in range(len(wset)):
            wdict[wset[num]]=num
        return wdict

    def list2nums(self,wlist):
        wdict = self.list2dict(wlist)
        output = []
        for w in wlist:
            output.append(wdict[w])
        return output

    def doc2numgrid(self, doc):
        keys = self.key_dict.keys()
        grid = []
        for key in keys:
            if key in doc:
                grid.append(self.key_dict[key])
            else:
                grid.append(0)
        return grid  

    def sklearn_inputs(self,table_name,text_column,category,keys_table,key_col,key_id):
        self.set_keydict(keys_table, key_col, key_id)
        query = "select "+text_column+", "+category+", to_tsvector("+text_column+") from "+table_name+" where "+category+" is not Null"
        results = self.wgrid.db_query(query)

        comments = []
        wcomments = []
        categories = []
        for row in results:
            wcomments.append(row[0])
            comments.append(self.doc2numgrid(row[0]))
            categories.append(row[1])

        

        comments = numpy.array(comments)
        ncategories = numpy.array(self.list2nums(categories))
        wcategories = numpy.array(categories)
        self.sk_inputs = {'text':comments,'cat_no':ncategories,'cat_text':wcategories,'wtext':wcomments}
        return self.sk_inputs

    def classify_data(self, model):
        predicted = []
        print self.sk_inputs.keys()
        for row in self.sk_inputs['text']:
            predicted.append(model.predict(row))       
        self.sk_inputs['predict'] = predicted

    def check_accuracy(self):
        return numpy.mean(self.sk_inputs['predict'] == self.sk_inputs['cat_no'])
        
    def sk_model(self,table_name,text_column,category,keys_table,key_col,key_id,index):
        self.sk_inputs = self.sklearn_inputs(table_name,text_column,category,keys_table,key_col,key_id)
        
        from sklearn import svm
        clf = svm.SVC(gamma=0.001, C=100.)
        clf.fit(self.sk_inputs['text'][:index],self.sk_inputs['cat_no'][:index])
        self.classify_data(clf)
        return clf

    def nltk_grid(self,sentence):
        keys = self.key_dict.keys()
        word_grid = {}
            

    def nltk_model(self,table_name,text_column,category,keys_table,key_col,key_id,index):
        self.sk_inputs = self.sklearn_inputs(table_name,text_column,category,keys_table,key_col,key_id)

        sentences = self.sk_inputs['wtext']
        

        

sksql = sk_sql(database,user,password,host,port)
sk_model = sksql.sk_model(table_name,text_column,category,keys_table,key_col,key_id,60)


print sk_model.predict(sksql.sk_inputs['text'][65])
print sksql.sk_inputs['predict'][65]
print sksql.sk_inputs['cat_text'][65]
print sksql.check_accuracy()


sk2 = sk_sql(database,user,password,host,port)
sk2m = sk2.sk_model(table_name,text_column,category,keys_table2,key_col,key_id,60)

print ""
print sk2m.predict(sk2.sk_inputs['text'][65])
print sk2.sk_inputs['predict'][65]
print sk2.sk_inputs['cat_text'][65]
print sk2.check_accuracy()

