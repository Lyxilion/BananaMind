# coding: utf8
# !/usr/bin/env python
from urllib.request import Request, urlopen
import json
import re
import os

# Uncomment line below if SSL error (ugly workaround)
"""
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
"""

# the separator use by windows '\' or Linux '/'
sep = "\\"   # Windows
# sep = "/"  # Linux

# Arguments
# -h : help
# -k : keywords (required), the keywords to search for
# -l : limit (optional default:500), limit of images to download
# -n : name (optional default:default), name of the output dir_path
# -m : mode (optional default:1), the mode of the request (1 : 5 request period of 1 year, 2 : 60 request 1 each month for 5 years)
# each argument must be follow by value between '"'
# example : -k "banana -juice" -n "Banana" -m "2"

# Google HANDBOOK :
# utiliser des operateur comme "poulpe -cuisine" pour suprimmer les images non voulue dès la recherche
# https://support.google.com/websearch/answer/2466433?hl=en

# JSON HANDBOOK :
# "pt"      name
# "ou"      link
# "ity"     file format
# "ow"      width
# "oh"      height


def commandProcessor(user_input: str):
    """
        the input processor
    :param user_input: a command input
    :type user_input: str
    :return: the keywords / the name of dir_path / the images' limit
    :rtype: list / str / int
    """
    time_scale = [
        "&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2019%2Ccd_max%3A7%2F30%2F2019",
        "&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2018%2Ccd_max%3A12%2F31%2F2018",
        "&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2017%2Ccd_max%3A12%2F31%2F2017",
        "&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2016%2Ccd_max%3A12%2F31%2F2016",
        "&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2015%2Ccd_max%3A12%2F31%2F2015"
    ]
    dir_path = "default"
    limit = 500
    keywords = False
    rep = re.findall(r'(-[klnm]) ?"([a-zA-Z0-9-_ ]*)"', user_input)
    if user_input == "-h" or user_input == "-help":
        print("-k : keywords (required), the keywords to search for.")
        print("-l : limit (optional default:500), limit of images to download the actual number is the int(limit/request)*requets, expect lower value")
        print("-n : name (optional default:default), name of the output directory")
        print("-m : mode (optional default:1, accepted_values:1, 2), the number of requests (1 : 5 request period of 1 year, 2 : 60 request 1 each month for 5 years)")
        print("""each argument must be follow by a value between '"'""")
        print("""example : -k "banana -juice" -n "Banana" """)
        return False, False, False, False
    for e in rep:
        if e[0] == "-k":
            if len(e[1]) > 0:
                keywords = e[1].split(" ")
            else:
                print('Need keywords')
                return False, False, False, False
        if e[0] == "-n":
            if len(e[1]) > 0:
                dir_path = e[1]
            else:
                print('Need valid name')
                return False, False, False, False
        if e[0] == "-l":
            if len(e[1]) > 0:
                if int(e[1]) <= 5000:
                    try:
                        limit = int(e[1])
                    except Exception as e:
                        print(e)
                else:
                    print("Impossible number of image (max:500)")
                    return False, False, False, False
            else:
                print('Need valid limit')
                return False, False, False, False
        if e[0] == "-m":
            if len(e[1]) > 0:
                if e[1] == "1":
                    pass
                elif e[1] == "2":
                    time_scale = []
                    days = ["31", "28", "31", "30", "31", "30", "31", "31", "30", "31", "30", "31"]
                    for i in range(5):
                        for j in range(12):
                            time_scale.append("&tbs=cdr%3A1%2Ccd_min%3A" + str(j + 1) + "%2F1%2F201" + str(i + 5) + "%2Ccd_max%3A" + str(j + 1) + "%2F" + days[j] + "%2F201" + str(i + 5))
                    print(time_scale)
                else:
                    print("Not a valid mode, use 1 or 2")
                    return False, False, False, False
    if not keywords:
        print("-k is required")
        return False, False, False, False
    return keywords, dir_path, limit, time_scale


def formatRequest(keywords: list, time: str):
    """
        Transform a list of keywords in a valid google images search URL
    :param keywords: a list of the keywords to search
    :type keywords: list
    :param time: a valid google get variable of a period of time
    :type time: str
    :return: a valid google images search URL
    :rtype: str
    """
    request = "https://www.google.com/search?tbm=isch&q="
    for e in keywords:
        request += e+"+"
    return request[:-1] + time


def findNextLink(page: str):
    """
        Find in the HTML code the first JSON of an images and loads it.
    :param page: the HTML code of the page
    :type page: str
    :return: JSON of the images / the place of the final char of the JSONin the page
    :rtype: dict / int
    """
    start_line = page.find('class="rg_meta notranslate">')      # the name of the div containing the json code
    if start_line == -1:                                        # check if there is no more links in the code
        print("No more links")
        return "No more links", None
    else:
        start_object = page.find('{', start_line + 1)
        end_object = page.find('</div>', start_object + 1)
        object_raw = str(page[start_object:end_object])
        final_object = loadJson(object_raw)                     # use custom function to repair and load JSON
        return final_object, end_object


def loadJson(s: str):
    """
        Repair and load a JSON tht might be broken by " or ,
    :param s: a JSON string
    :type s: str
    :return: a JSON repaired and loaded
    :rtype: dict
    """
    i = 0                    # Counter use by the fail safe if it's not reparable
    result = None
    while True or i > len(s):     # Failsafe : number of check greater than len of the string
        try:
            result = json.loads(s)
            break  # parsing worked -> exit loop
        except Exception as e:
            # this will use a regex on the exeption string to find the emplacement of the unexpected '"'
            # "Expecting , delimiter: line 34 column 54 (char 1158)"
            # position of unexpected character after '"'
            unexp = int(re.findall(r'\(char (\d+)\)', str(e))[0])
            # position of unescaped '"' before that
            unesc = s.rfind(r'"', 0, unexp)
            s = s[:unesc] + r'\"' + s[unesc + 1:]
            # position of correspondig closing '"' (+2 for inserted '\')
            closg = s.find(r'"', unesc + 2)
            s = s[:closg] + r'\"' + s[closg + 1:]
        i += 1
    return result


def formatName(img_object: dict):
    """
        Check if the filename is available, change it if not
    :param img_object: a JSON containing the information of the images
    :type img_object: dict
    :return: a valid name for the file
    :rtype: str
    """
    name = "downloads" + sep + dir_path + sep + str(img_object["ow"]) + "x" + str(img_object["oh"]) + "." + img_object["ity"]
    nameNotOk = True
    number = 2
    while nameNotOk:
        try:
            with open(name):
                name = "downloads" + sep + dir_path + sep + str(img_object["ow"]) + "x" + str(img_object["oh"]) + " (" + str(number) + ")." + img_object["ity"]
                number += 1
        except IOError:
            nameNotOk = False
    return name


def downloadImage(img_object: dict):
    """
        Download a images from a JSON
    :param img_object: a JSON containing the information of the images
    :type img_object: dict
    :return: True if download works False otherwise
    :rtype: bool
    """
    i = 0
    try:
        req = Request(img_object['ou'])
        response = urlopen(req)
        data = response.read()
        response.close()

        output = open(formatName(img_object), 'wb')
        output.write(data)
        output.close()
        i += 1
        return True
    except Exception as e:
        print("an error as occurred : " + str(e))
        return False


def createDir(dir_path: str):
    """
        Create a dir_path
    :param dir_path: name of the dir_path
    :type dir_path: str
    :return: 0
    """
    badChar = ['"', "*", "/", ":", "<", ">", "?", "\\", "|"]
    for e in badChar:
        dir_path = dir_path.replace(e, "")
    try:
        os.mkdir("downloads" + sep + dir_path)
    except OSError:
        print("Directory already exist")
    else:
        print("dir_path " + dir_path + " was created")


# __MAIN LOOP__ #
print("BananaCrawler 1.0\n-h for help")
keywords, dir_path, limit, time_scale = False, False, False, False
while not keywords:
    command = input("$")
    keywords, dir_path, limit, time_scale = commandProcessor(command)

createDir(dir_path)
page = ""
req_limit = int(limit / len(time_scale))
links = []
for j in range(len(time_scale)):
    print("----------------------")
    print("Request "+str((j+1))+" out of "+str(len(time_scale)))
    req = Request(formatRequest(keywords, time_scale[j]), headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})
    page = urlopen(req).read().decode()
    print("Request Success!")
    print("Searching for Links...")
    for i in range(req_limit):
        img_object, end = findNextLink(page)
        if img_object == "No more links":
            break
        else:
            links.append(img_object)
            page = page[end:]
    print("Done")
print("----------------------")
print(str(len(links))+" links found!")
print("----------------------")
print("Start Download...")
count = 0
for i in range(len(links)):
    if i % 10 == 0:
        print(str(i) + " out of " + str(len(links)))
    if downloadImage(links[i]):
        count += 1
print("Download finished")
print(str(count) + "/" + str(len(links)) + " images downloaded")
