from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import json
import time
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context




def downloadImage(object):
    req = Request(object['ou'])
    response = urlopen(req)
    data = response.read()
    response.close()
    #TODO suprimerles caractere pas utilisable dans un fichier
    #TODO gerer ereur 403 FORBIDEN
    #todo fix json json.decoder.JSONDecodeError: Expecting ',' delimiter: line 1 column 313 (char 312)
    output_file = open("image\\"+str(time.time())+"."+object["ity"], 'wb')
    output_file.write(data)
    output_file.close()

req = Request("https://www.google.com/search?tbm=isch&q=poulpe",headers = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})
soup = urlopen(req).read().decode()
#soup = BeautifulSoup(response.read(), 'html.parser')
#print(soup.prettify())
#output_file = open("test.html", 'w')
#output_file.write(soup.prettify())
#output_file.close()

def findNextLink(rep):
    start_line = rep.find('class="rg_meta notranslate">')
    start_object = rep.find('{', start_line + 1)
    end_object = rep.find('</div>', start_object + 1)
    object_raw = str(rep[start_object:end_object])
    object_decode = bytes(object_raw, "utf-8").decode("unicode_escape")
    final_object = json.loads(object_decode)
    return final_object, end_object



links = []
for i in range(50):
    obj, end = findNextLink(soup)
    links.append(obj)
    soup=soup[end:]

for e in links :
    downloadImage(e)
text = "j'aimeles ponguin"
print(links)


