from recommender import RecommenderBase
import torch
import numpy as np

class MatrixFactorization(RecommenderBase):
    
    def __init__(self,K, D):
        super(MatrixFactorization, self).__init__()
        np.random.seed(42069)
        # prepare matrices

        # one-hot categorical matrix
        self.C = 5 #NUM_CLASSES, need to 0 index
        self.Cdat = torch.tensor(np.array([[0.0]*self.P for c in range(self.C)]), requires_grad=False)
        self.K = K # number of hidden attributes
        for i in range(self.P):
            self.Cdat[self.problems[i][1]-1][i] = 1.0

        # hmmm how do we encode time problem was released?
        # oh wait the IDS themselves lmao, normalised
        # encode 1st and 2nd power, also transpose
        t = []
        self.NUM_POWERS = 1
        for i in range(self.P):
            r = self.problems[i][0]/self.max_problem_id
            t.append([r**k for k in range(self.NUM_POWERS+1)])
        self.Tdat = torch.Tensor.t(torch.tensor(np.array(t), requires_grad = False))
        
        # target matrix
        self.Rdat = torch.tensor(np.array([[0.0]*self.P for c in range(self.N)]), requires_grad=False)
        
        for i in range(self.N):
            for j in self.ppl[i]:
                self.Rdat[i][self.pid_map[j]] = 1.0

        # random initialisation from N(0,1)
        # initialise category bias matrix
        
        self.Cmat = torch.tensor(np.random.randn(self.N, self.C), requires_grad=True)

        # initialise time bias matrix
        self.Tmat = torch.tensor(np.random.randn(self.N, 2), requires_grad=True)
        # initialise latent user attributes
        self.Umat = torch.tensor(np.random.randn(self.N, self.K), requires_grad=True)

        # initialise latent problem attributes
        self.Pmat = torch.tensor(np.random.randn(self.K, self.P), requires_grad=True)

        # optional: move to gpu
        self.flattenedR = torch.flatten(self.Rdat)
        print(f"Testing model with K = {self.K} and lambda = {D}")
        self.accuracy = []
        self.train(D)
    def train(self, decay=0.1):
        print("Beginning to train")
        # trains model with regularization decay 
        losses = []

        # lol can tune lr here too
        loss_fn = torch.nn.functional.binary_cross_entropy_with_logits
        optimizer = torch.optim.AdamW((self.Umat, self.Pmat, self.Tmat, self.Cmat), lr=0.05, weight_decay = decay)

        EPS = 10**(-6)
        prev_accuracy = 0
        for i in range(260):
            # sigmoid is just for nicing up the values, doesn't change order
    
            loss = loss_fn(torch.sigmoid(torch.flatten((self.Umat @ self.Pmat) + (self.Cmat @ self.Cdat)+\
                                                       (self.Tmat @ self.Tdat))), self.flattenedR)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            losses.append(loss.item())
            print(f"Iteration #{len(losses)}: Loss = {losses[-1]}") 
            #if len(losses) >= 2 and abs(losses[-1]-losses[-2]) < EPS:
            #    break
            #if len(losses) % 20 == 0:
            #    self.evaluate("cv_recent.txt")
        #print("used", i+1, "its")
        self.accuracy = self.evaluate("cv_recent.txt")

    def get_score(self, personId, problemId):
        return (self.Umat[personId] * self.Pmat[:,problemId]).sum().item() +\
               (self.Tmat[personId] * self.Tdat[:,problemId]).sum().item() +\
               self.Cmat[personId][self.problems[problemId][1]-1]

    def predict(self, personId, numValues):
        candidates = []
        res = []
        for i in range(self.P):
            if self.Rdat[personId][i] != 1:
                candidates.append([self.get_score(personId, i), self.problems[i][0]])
        candidates = sorted(candidates, key = lambda x: x[0])

        for i in range(1, numValues+1):
            if i > len(candidates):
                res.append(0)
            else:
                res.append(candidates[-i][1])
        return res
    
            
"""
K = [2,3,4,5,6,7]
D = [0.01,0.03,0.09,0.27,0.63]
res = []
for i in K:
    for j in D:
        X = MatrixFactorization(i,j)
        res.append([i,j,X.accuracy])

res = sorted(res, key = lambda x: x[2][0])[::-1]

# rank by accuracy
for elem in res:
    print(elem)
"""
X = MatrixFactorization(7,0.7)
#X.evaluate("cv_recent.txt",10,20,5)
X.evaluate("test_recent.txt",5,10,5)
#"""

