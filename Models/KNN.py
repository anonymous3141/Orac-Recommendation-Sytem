from recommender import RecommenderBase
import numpy as np
# look ma, template method pattern


class KNN(RecommenderBase):

    def __init__(self,K):
        super(KNN, self).__init__()
        self.tmp = self.ppl[:]
        self.K = K
        
    def hamming(self, s1, s2):
        return len(s1) + len(s2) - 2*len(set(s1).intersection(set(s2)))

    #override
    def predict(self, personId, numValues):
        self.tmp = sorted(self.tmp, key = lambda x: self.hamming(self.ppl[personId], x))
        already_done = set(self.ppl[personId])
        freq = [[0,i] for i in range(self.max_problem_id + 1)]
        for i in range(self.K):
            for j in self.tmp[i]:
                freq[j][0] += 1
        freq = list(filter(lambda x: x[1] not in already_done, sorted(freq, key = lambda x: x[0])))
        res = []
        for i in range(1, numValues+1):
            res.append(freq[-i][1])
        return res
            
# Tune hyperparameters
def tune():
    for i in [1,2,4,8,16,32,64,128,256,512,1024,2048]:
        print(f"Testing K={i}")
        X = KNN(i)
        X.evaluate(test_file = "cv_recent.txt")
            
# Conclusion: K = 750 (or anything from 512 to 1024) best
# Very little variance, test accuracy ~ cross-validation accuracy
X = KNN(750)
X.evaluate("cv_recent.txt",10,20)
X.evaluate("test_recent.txt", 5, 10)

#49.4% - 62% accuracy
