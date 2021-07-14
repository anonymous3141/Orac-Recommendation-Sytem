"""
TODO:
- Map users to integers (for convinience & data privacy)
- Remove private problems from recent_solves
- Remove users who have not done problems recently
- Create for each user its solved problems
- i.e Create train set & test clickthrough set
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

def clean(s):
    return s.replace(" ","").replace("\n","")

# read in public problem as [class, ID]
# some aio problems appear in both senior and junior lists. Must filter out
def read_problems():
    raw = np.array(pd.read_csv("problems.csv"))
    seen = [0]* 1200

    processed = []
    for i in raw:
        if seen[i[1]]:
            continue
        else:
            seen[i[1]] = True
            processed.append(i)
    return processed

# read in list users
def read_people():
    k = open("people.txt","r")
    ppl =[]
    while True:
        person = clean(k.readline())

        if person != "":
            ppl.append(person)
        else:
            break
    ppl = list(set(ppl))
    k.close()
    return ppl



# read in solves
def read_solves(pplId):
    # pplId maps username to Id, contiguous and 0 indexed
    k = open("public_solves.txt","r")
    slvArr = [[] for i in range(len(pplId))]

    while True:
        problem_info = clean(k.readline()).split(":")
        if problem_info[0] == "":
            break
        problemId = int(problem_info[0])
        solvers = list(map(lambda x: pplId[x], problem_info[1].split(',')))
        for user in solvers:
            slvArr[user].append(problemId)

    # TODO: print stats
    k.close()
    return slvArr


# read in recent solves

def read_recent_solves(pplId):
    k = open("recent_solves.txt","r")
    recentArr = [[] for i in range(len(pplId))]
    N = 0
    P = 0
    while True:
        person_info = clean(k.readline()).split(":")
        if person_info[0] == "":
            break
        person = person_info[0]
        #print(person_info)
        if len(person_info[1]) > 0:
            solves = [int(c) for c in person_info[1].split(',')]
            recentArr[pplId[person]] = solves
    # TODO: print stats
    k.close()

    return recentArr

def readall_and_clean():
    problems = read_problems()
    problemSet = set()
    for p in problems:
        problemSet.add(p[1])
    
    people = read_people()
    pplId = {}
    
    for i in range(len(people)):
        pplId[people[i]] = i
    #print(pplId)    
    solves = read_solves(pplId)
    recents = read_recent_solves(pplId)

    #print(f"{sum([len(c) for c in recents])} recent Solves before removing private solves (capped at 30)")
    for i in range(len(recents)):
        recents[i] = list(filter(lambda x: x in problemSet, recents[i]))
    

    return solves, recents, problems

def describe(solves, recents, problems):
    print(f"{sum([len(c) for c in recents])} recent Solves after removing private solves (capped at 30)")
    print(f"{sum([len(c) for c in solves])} total Solves")
    print(f"{len(problems)} Public Problems")
    print(f"{len(solves)} People who has solved 1 public problem")
    print(f"{len(list(filter(lambda x:x>0,[len(c) for c in recents])))} People with recent solves")
    #print(solves)
    #print(recents)
    # Print Debug Aggregates
    fig, ax = plt.subplots(3,1)
    solveFreq = [len(c) for c in solves]
    recentFreq = [len(c) for c in recents]

    # number of total public solves per person
    ax[0].hist(solveFreq, bins = 100) #ax[0,0] if we used 2d array
    ax[0].set_title("Histogram of number of public solves per person")
    # number of recent public solves per person who has at least solved 1, capped at 30
    ax[1].hist(list(filter(lambda x:x>0,recentFreq)), bins = 30)
    ax[1].set_title("Histogram of number of recent public solves per person, capped at 30")
    # scatter of total vs recent solves
    ax[2].scatter(solveFreq, recentFreq)
    ax[2].set_title("Number of solves vs Number of recent solves per person")
    plt.show()
    


def write(file, d):
    # format
    # userId: list of problems solved, seperated by comma
    # 1 user per line
    l = open(file,"w")
    if type(d) == dict:
        #write dict
        for i, (personId, solves) in enumerate(d.items()):
            line = str(personId) + ": " + ",".join([str(c) for c in solves])
            l.write(line+"\n")
    else:
        #write array
        for personId in range(len(d)):
            line = str(personId) + ": " + ",".join([str(c) for c in d[personId]])
            l.write(line+"\n")
    l.close()

def make_datasets(solves, recents, problems):
    # For each person with recent solves, we choose min(#recent, ceil(#publicSolves/2), 20) such problems
    # at random. these problems will be our metric for testing clickthrough rate
    num_tests = []
    num_users = len(solves)
    for i in range(num_users):
        num_solves = len(solves[i])
        num_tests.append(min([(num_solves+1)//2, len(recents[i]), 20]))
    relevant = list(filter(lambda x: x>0,num_tests))
    print(sum(relevant), len(relevant))
    #plt.hist(relevant, bins=20)
    #plt.show()

    # we will allocate each person with things to test randomly to the cv set or test set with 50% chance
    # The people used in testing will have their solves, minus the ones for testing, used in training
    newSets = [{}, {}] #cv, test
    count = [0,0]
    new_solves = []
    for i in range(num_users):
        tests = []
        if num_tests[i] > 0:
            x = random.randint(0,1)
            count[x] += num_tests[i]
            random.shuffle(recents[i])
            tests = recents[i][:num_tests[i]]
            newSets[x][i] = tests
        tests_as_set = set(tests)
        new_solves.append(list(filter(lambda x: x not in tests_as_set, solves[i][:])))
    print("Tests distribution:", count)
    if abs(count[1]-count[0]) <= 100:
        write("train_solves.txt", new_solves)
        write("cv_recent.txt", newSets[0])
        write("test_recent.txt", newSets[1])
    

def clean_problem_list():
    X = read_problems()
    l = open("cleaned_problems.txt","w")
    for i in range(len(X)):
        l.write(str(X[i][1]) + " "+str(X[i][0])+"\n")
    l.close()
    
#describe(*readall_and_clean())
#make_datasets(*readall_and_clean())
clean_problem_list()
