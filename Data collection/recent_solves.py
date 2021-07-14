import aiohttp
import asyncio
from bs4 import BeautifulSoup

# Gets soup. Soup is an abstract representation of the HTML that has already been nicely parsed. 
# Has plenty of nice helper functions


# This code takes a range of 1000 users on the list
# It pulls all the IDs of their solves since CRITICAL_YEAR CRITICAL_MONTH (09-2020)
# It does not check if the solved ids are public

recent_solves_dict = {}

def read_people():
    k = open("people.txt","r")
    ppl =[]
    while True:
        person = k.readline()
        person = person.replace(" ","")
        person = person.replace("\n","")
        if person != "":
            ppl.append(person)
        else:
            break
    return ppl

def extract_pid(url):
    # return string
    tmp = url.split("problemid=")
    return int(tmp[1].split('"')[0])

def isvaliddate(s):
    # check if is yyyy-mm-dd
    CRITICAL_YEAR = 2020
    CRITICAL_MONTH = 9
    if len(s) != 10 or s.count('-') != 2:
        return 0
    else:
        date = [int(c) for c in s.split('-')]
        if date[0] > CRITICAL_YEAR or (date[0] == CRITICAL_YEAR and date[1] >= CRITICAL_MONTH):
            return 1
        else:
            return 2
async def get_soup(session,url):
    print("Retrieved",url)
    async with session.get(url) as req:
        #print(req.status)
        if req.status == 200:
            return BeautifulSoup(await req.text(), 'html.parser')
    return None

async def process_url(session,username):
    url = "http://orac.amt.edu.au/lorikeet/user/" + username
    soup = await get_soup(session,url)
    if (soup != None):        
        # Find first sub_data dataframe, it contains recent solves
        # Then get all links, these are links to other problems
        result = soup.find(class_ = "sub_data").find_all('a')
        fragments = soup.find(class_="sub_data").text.split()
        #print(fragments)
        num_valid_solves = 0
        for i in fragments:
            res = isvaliddate(i)
            if res == 1:
                num_valid_solves += 1
            elif res == 2: break

        #print(username, num_valid_solves)
        slvs = []
        for link in result:
            if "lorikeet" in link.attrs['href']: #ignore lorikeet urls
                continue
            if num_valid_solves == 0:
                break
            slvs.append(extract_pid(link.attrs['href']))
            num_valid_solves -= 1
        #print(slvs)
        recent_solves_dict[username] = slvs

# basically our main function, we have to put it in async so we can go faster
async def do_stuff(l,r):

    # The Contents of LORIKEET_HEADER is redacted as it contains sensitive info
    # A backchannel needing login was used for easier scraping of data
    # All data is public, but the backchannel is easier
    # TO fill in header see second answer from below
    # https://stackoverflow.com/questions/23102833
    # i.e how-to-scrape-a-website-which-requires-login-using-python-and-beautifulsoup
    # Use this tool: https://curl.trillworks.com/
    # For privacy concerns the raw results of recent solves is redacted
    LORIKEET_HEADER =  {}
    async with aiohttp.ClientSession(headers=LORIKEET_HEADER) as session:
        # we make an array of all the tasks 
        tasks = []
        """
        tasks.append(process_url(session,"anonymous"))
        tasks.append(process_url(session,"spdskatr"))
        tasks.append(process_url(session,"thyroid"))
        """
        for person in read_people()[l:r]:
             tasks.append(process_url(session,person))

        
        results = await asyncio.gather(*tasks)
    
# Actually call do_stuff

def execute(x):
    # scraping everything at once gets time limit exceed errors
    # groups of 1000 work just fine
    BLK = 1000 # x = 0,1,2,3,4
    asyncio.run(do_stuff(x*BLK, (x+1)*BLK))
    print(recent_solves_dict)

    # write to file
    l = open(f"recent{x}.txt","w")
    for i, (person, solves) in enumerate(recent_solves_dict.items()):
        line = str(person) + ": " + ",".join([str(c) for c in solves])
        l.write(line+"\n")
        
    l.close()

execute(0)
