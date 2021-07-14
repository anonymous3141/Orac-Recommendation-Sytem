# framework for testing the model

class RecommenderBase:
    def clean(self, s):
        return s.replace(" ","").replace("\n","")
    def __init__(self):
        k = open("train_solves.txt")
        self.ppl = []
        self.max_problem_id = 0
        self.N = 0 # number of users, users 0 indexed

        # read training user set
        while True:
            user = self.clean(k.readline())
            if user == "":
                break
            self.N  += 1
            slvstring = user.split(":")[1].split(",")
            if slvstring[0] != "":
                self.ppl.append([int(c) for c in slvstring])
                self.max_problem_id = max(self.max_problem_id, max(self.ppl[-1]))
            else:
                self.ppl.append([])
        k.close()

        # read problem list
        self.problems = []
        k2 = open("cleaned_problems.txt","r")
        while True:
            line = k2.readline()
            if line == "":
                break
            self.problems.append([int(c) for c in line.split()])
        self.P = len(self.problems) # number of problems

        #coor compress for problems
        self.pid_map = {}
        for i in range(self.P):
            self.pid_map[self.problems[i][0]] = i

    def predict(self, personId, numValues):
        # returns top numValues predictions to personId
        # it will be overriden
        # values must be returned in the order of their likelihood
        return [0]*numValues

    def evaluate(self, test_file, THRESH_1=10, THRESH_2=20, THRESH_3 = 5):
        # test file contains test cases in form:
        # 1 user per line in form:
        # user_id: <comma seperated list of actual solves>
        # returns correct answers
        # Measure accuracy on top10 and top20 accuracy i.e (#in top 10 per prediction / # problems tested)
        # Another metric, the top N+5, is used. 
        # Okay, so we will have a decent metric and test
        num_solves = 0
        num_ppl = 0
        score_1 = 0
        score_2 = 0
        score_3 = 0
        LIMIT_CAP = 25
        k = open(test_file, 'r')
        while True:
            testcase = k.readline()
            if testcase == "":
                break
            num_ppl += 1
            [uid, slvs] = testcase.split(':')
            uid = int(uid)
            slvs = set([int(c) for c in slvs.split(',')])
            preds = self.predict(uid, LIMIT_CAP)
            pred_1 = set(preds[:THRESH_1])
            pred_2 = set(preds[:THRESH_2])
            pred_3 = set(preds[:THRESH_3 + len(slvs)])
            num_solves += len(slvs)
            score_1 += len(pred_1.intersection(slvs))
            score_2 += len(pred_2.intersection(slvs))
            score_3 += len(pred_3.intersection(slvs))
        print(f"Evaluated on file {test_file} with {num_ppl} Cases and {num_solves} solves")
        print(f"Top {THRESH_1} Accuracy: {score_1/num_solves}")
        print(f"Top {THRESH_2} Accuracy: {score_2/num_solves}")
        print(f"Top N+{THRESH_3} Accuracy: {score_3/num_solves}")
        return score_1/num_solves,score_2/num_solves,score_3/num_solves
    

def test():
    # dumb system
    x= RecommenderBase()
    x.evaluate("cv_recent.txt")


