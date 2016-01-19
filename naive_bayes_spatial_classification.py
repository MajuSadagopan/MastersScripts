import nltk
import random
import psycopg2 as psy

#========= Variables ==========
new_table = "bayes_new_training_set"
training_data = 'iht_trained_survey'
text_col = "dsc"
match_table_col = "match_tabl"
#========= Variables ==========

conn = psy.connect(database="region_waterloo", user="postgres", password="love2Learn",host="localhost", port="5433")
cur = conn.cursor()

table_query = "select gid into "+new_table+" from "+training_data+" where "+match_table_col+" is not NULL"
cur.execute(table_query)
conn.commit()


cur.execute("select distinct "+match_table_col+" from "+training_data+" where "+match_table_col+" is not NULL")
classifiers= cur.fetchall()
classes = [(row[0]) for row in classifiers]

cur.execute("select distinct on (keyword) array_agg(keyword) from query_keys group by keyword")
word_features = cur.fetchall()

for key_col in classes:

    query = "alter table "+new_table+" add column " + key_col + " boolean"
    cur.execute(query)
    conn.commit()
    
    retrieve_query = "select gid, "+text_col+",( "+match_table_col+" = %s) as boolean from "+training_data
    cur.execute(retrieve_query,[key_col])
    iht_all = cur.fetchall()
    documents=[]


    for row in iht_all:
        if row[1] is not None:
            documents.append((row[1].strip().lower().split(),row[2]))
    #random.shuffle(documents)




    def document_features(document):
        document_words = set(document)
        features = {}
        for word in word_features:
            word=word[0][0]
            features['contains({})'.format(word)] = (word in document_words)
        return features


    featuresets = [(document_features(d), c) for (d,c) in documents]


    train_set, test_set = featuresets[60:], featuresets[:60]
    classifier = nltk.NaiveBayesClassifier.train(train_set)

    print(key_col)
    print(nltk.classify.accuracy(classifier, test_set))
    print(classifier.show_most_informative_features(20))


    for row in iht_all:
        if row[1] is not None:
            result = classifier.classify(document_features(row[1].strip().lower().split()))
            if result is not None:
                query = "UPDATE "+new_table+" SET "+key_col+" = "+str(result)+" WHERE gid = "+str(row[0])
            #print(query)
            cur.execute(query)
            conn.commit()

cur.close()
conn.close()

