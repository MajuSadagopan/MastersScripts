import sklearn
import sklearn.datasets
from sklearn.feature_extraction.text import CountVectorizer

# =========== Variables =================
file_path = "C:\\Users\\Maju\\Downloads\\20news_bydate\\20news_bydate\\20news_bydate_train"
categories = ['alt.atheism', 'soc.religion.christian','comp.graphics','sci.med']


tw_train = sklearn.datasets.load_files(file_path, categories=categories)

count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(tw_train.data)
print "jim"
    
