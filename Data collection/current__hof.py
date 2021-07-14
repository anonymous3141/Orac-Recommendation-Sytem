import pandas as pd
import numpy as np
import aiohttp
import asyncio
from bs4 import BeautifulSoup
solves_dict = {} #pid: array of solver unames
def get_problems():
    FILE = "problems.csv"
    arr = np.array(pd.read_csv(FILE))
    return  arr
# Gets soup. Soup is an abstract representation of the HTML that has already been nicely parsed. 
# Has plenty of nice helper functions
async def get_soup(session,url):
    print("Retrieved",url)
    async with session.get(url) as req:
        if req.status == 200:
            return BeautifulSoup(await req.text(), 'html.parser')
    return None

async def process_url(session, pid):
    url = "http://orac.amt.edu.au/cgi-bin/train/fame_detail.pl?problemid="+str(pid)
    soup = await get_soup(session,url)
    if (soup != None):        
        # Look up the beautifulsoup documentation to see what you can do with this soup object
        result = soup.find(class_ = "index").text.split('problem.')[1].split(',') #the ppl is stored inside index
        """
        # go to the next sibling
        print (result.next_sibling)

        # ... a couple times
        print (result.next_sibling.next_sibling)
        print (result.next_sibling.next_sibling.next_sibling)
        print (result.next_sibling.next_sibling.next_sibling.next_sibling)

        # I am pretty sure a lot of times you want the .text attribute too
        """
        solves_dict[pid] = result
# basically our main function, we have to put it in async so we can go faster
async def do_stuff():
    async with aiohttp.ClientSession() as session:
        # we make an array of all the tasks 
        tasks = []
        problems = get_problems()
        #problems = [[1,1],[1,2],[1,3]] #for testing
        for problem in problems:
            tasks.append(process_url(session,problem[1]))
        # Note that at this point, not all the functions in tasks have returned yet. Hence we wait for it
        # by calling asyncio.gather
        # If process_url returns something then results will contain all the return values 
        
        results = await asyncio.gather(*tasks)
    
# Actually call do_stuff
asyncio.run(do_stuff())

set_people = set()
l = open("solves.txt","w")
for i, (problem, solves) in enumerate(solves_dict.items()):
    line = str(problem) + ": " + ",".join(solves)
    l.write(line+"\n")
    for person in solves:
        set_people.add(person)
l.close()

l2 = open("people.txt","w")
l2.write("\n".join(list(set_people)))
l2.close()
