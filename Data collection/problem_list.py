from bs4 import BeautifulSoup
import requests
k = open("problem_list.txt","r")
html = ""
while True:
    line = k.readline()
    html += line
    if line == "":
        break

soup = BeautifulSoup(html, 'html.parser')
list_elems = soup.find_all('a')
#print(list_elems)

# ACIO, challenge problems are ignored
CLASSES = {'simple':1, 'aio':2, 'aic':3, 'aiio':4, 'fario':5}
prob_list = []
link_tags = []

#print(soup)
    
for i in list_elems:
    #i is of type tag
    if "href" not in i.attrs:
        continue
    if "problemid" in i.attrs['href']:

        href = i['href']
        problem_class = 0
        for key in CLASSES.keys():
            if key in href:
                problem_class = CLASSES[key]
                break
        if problem_class == 0:
            #ignore acio, precamp & challenge
            continue

        # get problem id
        pid = int(href.split("problemid=")[1].split('"')[0])

        if problem_class == 5:
            print('yay')
            #check if problem is sliding scale, if so ignore
            #only farios have sliding scale
            URL = "http://orac.amt.edu.au/cgi-bin/train/fame_detail.pl?problemid="+str(pid)
            txt = requests.get(URL, stream=True).text
            identifier = "Congratulations to the top scorers!"

            if identifier in txt:
                continue
            
            
        prob_list.append([problem_class, pid])


def write_csv():
    import pandas as pd
    print(prob_list)
    l = open("problems.csv","w")
    l.write(pd.DataFrame(prob_list, columns=['problem class', 'id']).to_csv(index=False))
    l.close()

    
write_csv()
