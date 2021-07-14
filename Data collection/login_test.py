import requests
from bs4 import BeautifulSoup

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Authorization': 'Basic YW5vbnltb3VzOmJyZXhpdHN1Y2tz',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

URL = 'http://orac.amt.edu.au/lorikeet/user/harry'
response = requests.get(URL, headers=headers, verify=False)

bsText = BeautifulSoup(response.text, 'html.parser')
print(bsText)
