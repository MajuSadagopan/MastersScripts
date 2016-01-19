import nltk
import random

names={'female':['Lisa','Belle','Jasmine','Lucy','Melenie','Malathi'],'male':['Jim','Liam','Nigel', 'Micheal','Tim','Tom','Tarek']}

print('started')
def gender_feature(word):
    return{'last_letter':word[-1]}


labeled_names = ([(name, 'male') for name in names['male']]+[(name, 'female') for name in names['female']])

random.shuffle(labeled_names)

featuresets = [(gender_feature(n), gender) for (n, gender) in labeled_names]

train_set, test_set = featuresets[6:], featuresets[:6]


for train in train_set:
    print('train',train)

print

for test in test_set:
    print('test_set',test)


classifier = nltk.NaiveBayesClassifier.train(train_set)

print('Lisa is', classifier.classify(gender_feature('Lisa')))


print(nltk.classify.accuracy(classifier, test_set))

    
print(nltk.classify.accuracy(classifier, test_set))

print(classifier.show_most_informative_features(5))
