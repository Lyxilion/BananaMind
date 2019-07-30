# coding: utf8
# !/usr/bin/env python
from urllib.request import Request, urlopen
import json
import re
import os

# Uncomment line below if SSL error (workaround)
"""
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
"""

# the separator use by windows '\' or Linux '/'
sep = "\\"   # Windows
#sep = "/"   # Linux

timeScale = [
    "&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2019%2Ccd_max%3A7%2F30%2F2019",
    "&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2018%2Ccd_max%3A12%2F31%2F2018",
    "&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2017%2Ccd_max%3A12%2F31%2F2017",
    "&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2016%2Ccd_max%3A12%2F31%2F2016",
    "&tbs=cdr%3A1%2Ccd_min%3A1%2F1%2F2015%2Ccd_max%3A12%2F31%2F2015"
]

# Arguments
# -k : keywords (required), the keywords to search for
# -l : limit (optional default:500), limit of image to download
# -n : name (optional default:default), name of the output directory
# each argument must be follow by value between '"'
# example : -k "banana -juice" -n "Banana"

# Google HANDBOOK :
# utiliser des operateur comme "poulpe -cuisine" pour suprimmer les images non voulue dès la recherche
# https://support.google.com/websearch/answer/2466433?hl=en

# JSON HANDBOOK :
# "pt"      name
# "ou"      link
# "ity"     file format
# "ow"      width
# "oh"      height


def commandProcesor(input: str):
    """
        the input processor
    :param input: a command input
    :type input: str
    :return: the keywords / the name of directory / the images' limit
    :rtype: list / str / int
    """
    dir = "default"
    limit = 500
    keywords = False
    rep = re.findall(r'(-[khslrn]) ?"([a-zA-Z0-9- ]*)"', input)

    for e in rep:
        if e[0] == "-k":
            if len(e[1]) > 0:
                keywords = e[1].split(" ")
            else:
                print('Need keywords')
                exit()
        if e[0] == "-n":
            if len(e[1]) > 0:
                dir = e[1]
            else:
                print('Need valid name')
                exit()
        if e[0] == "-l":
            if len(e[1]) > 0:
                limit = int(e[1])
            else:
                print('Need valid limit')
                exit()
    if not keywords:
        print("-k is required")
        exit()
    return keywords, dir, limit


def formatRequest(keywords: list, time: str):
    """
        Transform a list of keywords in a valid google image search URL
    :param keywords: a list of the keyworkdto search
    :type keywords: list
    :param time: a valid google get variable of a period of time
    :type time: str
    :return: a valid google image search URL
    :rtype: str
    """
    request = "https://www.google.com/search?tbm=isch&q="
    for e in keywords:
        request += e+"+"
    request += time
    return request


def findNextLink(page: str):
    """
        Find in the HTML code the first JSON of an image and loads it.
    :param page: the HTML code of the page
    :type page: str
    :return: JSON of the image / the place of the final char of the JSONin the page
    :rtype: dict / int
    """
    start_line = page.find('class="rg_meta notranslate">')      # the name of the div contening the json code
    if start_line == -1:                                        # check if there is no more links in the code
        print("No more links")
        return "No more links", None
    else:
        start_object = page.find('{', start_line + 1)
        end_object = page.find('</div>', start_object + 1)
        object_raw = str(page[start_object:end_object])
        final_object = loadJson(object_raw)                     # use custom fonction to repair and load JSON
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


def formatName(object: dict):
    """
        Check if the filename is available, change it if not
    :param object: a JSON containing the information of the image
    :type object: dict
    :return: a valid name for the file
    :rtype: str
    """
    name = "downloads" + sep + dir + sep + str(object["ow"]) + "x" + str(object["oh"]) + "." + object["ity"]
    nameNotOk = True
    number = 2
    while nameNotOk:
        try:
            with open(name):
                name = "downloads" + sep + dir + sep + str(object["ow"]) + "x" + str(object["oh"]) + " (" + str(number) + ")." + object["ity"]
                number += 1
        except IOError:
            nameNotOk = False
    return name


def downloadImage(object: dict):
    """
        Download a image from a JSON
    :param object: a JSON containing the information of the image
    :type object: dict
    :return: True if download works False otherwise
    :rtype: bool
    """
    i = 0
    try:
        req = Request(object['ou'])
        response = urlopen(req)
        data = response.read()
        response.close()

        output = open(formatName(object), 'wb')
        output.write(data)
        output.close()
        i += 1
        return True
    except Exception as e:
        print("an error as occurred : " + str(e))
        return False
        # Error 403


def createDir(dir: str):
    """
        Create a directory
    :param dir: name of the directory
    :type dir: str
    :return: 0
    """
    badChar = ['"', "*", "/", ":", "<", ">", "?", "\\", "|"]
    for e in badChar:
        dir = dir.replace(e, "")
    try:
        os.mkdir("downloads" + sep + dir)
    except OSError:
        print("Directory already exist")
    else:
        print("directory " + dir + " was created")


# __MAIN LOOP__ #

command = input("$")
keywords, dir, limit = commandProcesor(command)
page = ""
for e in timeScale:
    print("Request...")
    req = Request(formatRequest(keywords, e), headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})
    page += urlopen(req).read().decode()
    print("Request Success!")
createDir(dir)
print("Searching for Links...")
links = []
for i in range(limit):
    object, end = findNextLink(page)
    if object == "No more links":
        break
    else:
        links.append(object)
        page = page[end:]
print(str(len(links))+" links found!")

print("Start Download...")
count = 0
for e in links:
    if downloadImage(e):
        count += 1
print("Download finished")
print(str(count) + "/" + str(len(links)) + " images downloaded")


# TODO LIST :
# TODO add related search
# TODO add search picture(photos) only ?
# TODO add EXIF checker ?
