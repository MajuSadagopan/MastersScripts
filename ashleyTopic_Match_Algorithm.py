import random,os

alpha = 0.1
beta = 0.1
K = 10
iter_num = 50
top_words = 20

wordmapfile  = 'wordmap_all.txt'
trnfile = "PM.txt"
modelfile_suffix = "result_minutes"

class Document(object):
    def __init__(self):
        self.words = []
        self.length = 0

class Dataset(object):
    def __init__(self):
        self.M = 0
        self.V = 0
        self.docs = []
        self.word2id = {}    # <string,int> dictionary
        self.id2word = {}    # <int, string> dictionary

    def writewordmap(self):
        with open(wordmapfile, 'w') as f:
            for k,v in self.word2id.items():
                f.write(k + '\t' + str(v) + '\n')

class Model(object):
    def __init__(self, dset):
        self.dset = dset

        self.K = K
        self.alpha = alpha
        self.beta = beta
        self.iter_num = iter_num
        self.top_words = top_words

        self.wordmapfile = wordmapfile
        self.trnfile = trnfile
        self.modelfile_suffix = modelfile_suffix

        self.p = []        # double type, store temp variants from sampling 
        self.Z = []        # M*doc.size()，topic-words distribution of the words 
        self.nw = []       # V*K，the distribution of word i on topic j 
        self.nwsum = []    # K，# of words topic j has 
        self.nd = []       # M*K，# of words doc i has that belong to topic j 
        self.ndsum = []    # M，# of words topic i has 
        self.theta = []    # doc - topic distribution 
        self.phi = []      # topic - word distribution 

    def init_est(self):
        self.p = [0.0 for x in xrange(self.K)]
        self.nw = [ [0 for y in xrange(self.K)] for x in xrange(self.dset.V) ]
        self.nwsum = [ 0 for x in xrange(self.K)]
        self.nd = [ [ 0 for y in xrange(self.K)] for x in xrange(self.dset.M)]
        self.ndsum = [ 0 for x in xrange(self.dset.M)]
        self.Z = [ [] for x in xrange(self.dset.M)]
        for x in xrange(self.dset.M):
            self.Z[x] = [0 for y in xrange(self.dset.docs[x].length)]
            self.ndsum[x] = self.dset.docs[x].length
            for y in xrange(self.dset.docs[x].length):
                topic = random.randint(0, self.K-1)
                self.Z[x][y] = topic
                self.nw[self.dset.docs[x].words[y]][topic] += 1
                self.nd[x][topic] += 1
                self.nwsum[topic] += 1
        self.theta = [ [0.0 for y in xrange(self.K)] for x in xrange(self.dset.M) ]
        self.phi = [ [ 0.0 for y in xrange(self.dset.V) ] for x in xrange(self.K)]

    def estimate(self):
        print 'Sampling %d iterations!' % self.iter_num
        for x in xrange(self.iter_num):
            print 'Iteration %d ...' % (x+1)
            for i in xrange(len(self.dset.docs)):
                for j in xrange(self.dset.docs[i].length):
                    topic = self.sampling(i, j)
                    self.Z[i][j] = topic
        print 'End sampling.'
        print 'Compute theta...'
        self.compute_theta()
        print 'Compute phi...'
        self.compute_phi()
        print 'Saving model...'
        self.save_model()

    def sampling(self, i, j):
        topic = self.Z[i][j]
        wid = self.dset.docs[i].words[j]
        self.nw[wid][topic] -= 1
        self.nd[i][topic] -= 1
        self.nwsum[topic] -= 1
        self.ndsum[i] -= 1

        Vbeta = self.dset.V * self.beta
        Kalpha = self.K * self.alpha

        for k in xrange(self.K):
            self.p[k] = (self.nw[wid][k] + self.beta)/(self.nwsum[k] + Vbeta) * \
                        (self.nd[i][k] + alpha)/(self.ndsum[i] + Kalpha)
        for k in range(1, self.K):
            self.p[k] += self.p[k-1]
        u = random.uniform(0, self.p[self.K-1])
        for topic in xrange(self.K):
            if self.p[topic]>u:
                break
        self.nw[wid][topic] += 1
        self.nwsum[topic] += 1
        self.nd[i][topic] += 1
        self.ndsum[i] += 1
        return topic

    def compute_theta(self):
        for x in xrange(self.dset.M):
            for y in xrange(self.K):
                self.theta[x][y] = (self.nd[x][y] + self.alpha) \
                                   /(self.ndsum[x] + self.K * self.alpha)

    def compute_phi(self):
        for x in xrange(self.K):
            for y in xrange(self.dset.V):
                self.phi[x][y] = (self.nw[y][x] + self.beta)\
                                 /(self.nwsum[x] + self.dset.V * self.beta)

    def save_model(self):
        with open(self.modelfile_suffix+'.theta', 'w') as ftheta:
            for x in xrange(self.dset.M):
                for y in xrange(self.K):
                    ftheta.write(str(self.theta[x][y]) + ' ')
                ftheta.write('\n')
        with open(self.modelfile_suffix+'.phi', 'w') as fphi:
            for x in xrange(self.K):
                for y in xrange(self.dset.V):
                    fphi.write(str(self.phi[x][y]) + ' ')
                fphi.write('\n')
        with open(self.modelfile_suffix+'.twords','w') as ftwords:
            if self.top_words > self.dset.V:
                self.top_words = self.dset.V
            for x in xrange(self.K):
                ftwords.write('Topic '+str(x)+'th:\n')
                topic_words = []
                for y in xrange(self.dset.V):
                    topic_words.append((y, self.phi[x][y]))
                #quick-sort
                topic_words.sort(key=lambda x:x[1], reverse=True)
                for y in xrange(self.top_words):
                    word = self.dset.id2word[topic_words[y][0]]
                    ftwords.write('\t'+word+'\t'+str(topic_words[y][1])+'\n')
        with open(self.modelfile_suffix+'.tassign','w') as ftassign:
            for x in xrange(self.dset.M):
                for y in xrange(self.dset.docs[x].length):
                    ftassign.write(str(self.dset.docs[x].words[y])+':'+str(self.Z[x][y])+' ')
                ftassign.write('\n')
        with open(self.modelfile_suffix+'.others','w') as fothers:
            fothers.write('alpha = '+str(self.alpha)+'\n')
            fothers.write('beta = '+str(self.beta)+'\n')
            fothers.write('ntopics = '+str(self.K)+'\n')
            fothers.write('ndocs = '+str(self.dset.M)+'\n')
            fothers.write('nwords = '+str(self.dset.V)+'\n')
            fothers.write('liter = '+str(self.iter_num)+'\n')

def readtrnfile():
    print 'Reading train data...'
    with open(trnfile, 'r') as f:
        docs = f.readlines()

    dset = Dataset()
    items_idx = 0
    for line in docs:
        if line != "":
            tmp = line.strip().split('\t')
            #genereate a document object
            doc = Document()
            for item in tmp:
                if dset.word2id.has_key(item):
                    doc.words.append(dset.word2id[item])
                else:
                    dset.word2id[item] = items_idx
                    dset.id2word[items_idx] = item
                    doc.words.append(items_idx)
                    items_idx += 1
            doc.length = len(tmp)
            dset.docs.append(doc)
        else:
            pass
    dset.M = len(dset.docs)
    dset.V = len(dset.word2id)
    print 'There are %d documents' % dset.M
    print 'There are %d items' % dset.V
    print 'Saving wordmap file...'
    dset.writewordmap()
    return dset

def lda():
    dset = readtrnfile()
    model = Model(dset)
    model.init_est()
    model.estimate()

if __name__=='__main__':
    lda()
