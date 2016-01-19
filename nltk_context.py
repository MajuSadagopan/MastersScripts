import sklearn
import sklearn.datasets

categories =['alt.atheism','soc.religion.christian','comp.graphics','sci.med']

from sklearn.datasets import fetch20newsgroup

twenty_train = fetch_20newsgroups(subset='train', categories=categories, shuffle=True, random_state=42)

print twenty_train.target_names
