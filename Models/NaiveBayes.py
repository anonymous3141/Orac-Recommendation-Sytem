from recommender import RecommenderBase
import numpy as np
# look ma, template method pattern
# Laplace smoothed Naive Bayes

class NaiveBayes(RecommenderBase):
    def __init__(self):
        super(NaiveBayes, self).__init__()
        self.Freq = [[[1,1] for c in range(self.P)] for d in range(self.P)]
        self.numSolvers = [0]*self.P
        self.Pr = [[[0,0] for c in range(self.P)] for d in range(self.P)]
        self.PrSolve = [0]*self.P
        # Freq[i][j][0] = Num(solved i and not solved j)
        # Freq[i][j][1] = Num(solved i and solved j) 
        # Pr[i][j][0] = log((Freq[i][j][0]+1)/(# solved i+2)
        # This is Laplacian smoothing
        # PrSolve[i] = log(# solved i / # users)

        for i in range(self.N):
            #print(np.max(np.array(self.Freq)))
            done = set(self.ppl[i])
            for solved_problem in self.ppl[i]:
                for p in self.problems:
                    problem = p[0]
                    #print("Increment", self.pid_map[solved_problem],self.pid_map[problem],problem in done, "by person", i)
                    self.Freq[self.pid_map[solved_problem]][self.pid_map[problem]][problem in done] += 1
                self.numSolvers[self.pid_map[solved_problem]] += 1
            

        for i in range(self.P):
            for j in range(self.P):
                #print(self.Freq[i][j][0],(2+self.numSolvers[i]))
                self.Pr[i][j][0] = np.log(self.Freq[i][j][0]/(2+self.numSolvers[i]))
                self.Pr[i][j][1] = np.log(self.Freq[i][j][1]/(2+self.numSolvers[i])) 
        
        for i in range(self.P):
            self.PrSolve[i] = np.log(self.numSolvers[i]/self.N)
    #override
    def predict(self, personId, numValues):
        doneProblems = set(map(lambda x: self.pid_map[x], self.ppl[personId]))
        likelihood = [[self.PrSolve[i],i] for i in range(self.P)]
        for i in range(self.P):
            isDone = i in doneProblems 
            for j in range(self.P):
                likelihood[j][0] += self.Pr[j][i][isDone]
        likelihood = list(filter(lambda x: x[1] not in doneProblems, sorted(likelihood, key=lambda x: x[0])))
        res = []

        #probability seeems scuffed btw
        #print(likelihood)
        for i in range(1, numValues+1):
            if i <= len(likelihood):
                res.append(self.problems[likelihood[-i][1]][0])
            else:
                res.append(0)
        return res

X = NaiveBayes()
X.evaluate("cv_recent.txt")
X.evaluate("test_recent.txt",5,10)
            
