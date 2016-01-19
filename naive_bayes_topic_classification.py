import nltk
import random
import psycopg2 as psy

#========= Variables ==========
new_table = "bayes_output"

conn = psy.connect(database="region_waterloo", user="postgres", password="love2Learn",host="localhost", port="5433")
cur = conn.cursor()

table_query = "select no into "+new_table+" from iht_all_xls"
cur.execute(table_query)
conn.commit()


cur.execute("select * from classifiers")
classifiers= cur.fetchall()
classes = [(row[0]) for row in classifiers]


for key_col in classes:

    query = "alter table "+new_table+" add column " + key_col + " boolean"
    cur.execute(query)
    conn.commit()
    
    retrieve_query = "select no, comment,( "+key_col+" is not NULL) lighting from iht_all_xls"
    cur.execute(retrieve_query)
    iht_all = cur.fetchall()
    documents=[]


    for row in iht_all:
        if row[1] is not None:
            documents.append((row[1].strip().lower().split(),row[2]))
    #random.shuffle(documents)


    cur.execute("select array_agg(word) from iht_common_words")
    words = cur.fetchall()
    word_features = words[0][0]


    def document_features(document):
        document_words = set(document)
        features = {}
        for word in word_features:
            features['contains({})'.format(word)] = (word in document_words)
        return features


    featuresets = [(document_features(d), c) for (d,c) in documents]


    train_set, test_set = featuresets[400:], featuresets[:400]
    classifier = nltk.NaiveBayesClassifier.train(train_set)

    print(key_col)
    #print(nltk.classify.accuracy(classifier, test_set))
    #print(classifier.show_most_informative_features(20))


    for row in iht_all:
        if row[1] is not None:
            query = "UPDATE bayes_output SET "+key_col+" = %s WHERE no = %s"
            result = classifier.classify(document_features(row[1].strip().lower().split()))
            query = "UPDATE bayes_output SET "+key_col+" = "+str(result)+" WHERE no = "+str(row[0])
            #print(query)
            cur.execute(query)
            conn.commit()

