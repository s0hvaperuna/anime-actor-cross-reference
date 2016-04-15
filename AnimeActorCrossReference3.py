#!/usr/bin/python3
import sys
import pprint
import requests
import lxml
from bs4 import BeautifulSoup
from threading import Thread

def split(a, n):
    k, m = int(len(a) / n), len(a) % n
    sliced = []
    for i in range(n):
        sliced += [a[i * k:(i + 1) * k]]
    sliced += [a[-m]]
    return sliced

def main():
    usr = input("MAL username: ")
    f = input("Save to file (y/n): ")

    r = requests.get('http://myanimelist.net/malappinfo.php?u=' + str(usr) + '&status=all&type=anime', headers={"user-agent": "iMAL-iOS"})

    soup = BeautifulSoup(r.text, "lxml-xml")
    titles = soup.find_all('series_title')
    ids = soup.find_all('series_animedb_id')

    total_watched = int(soup.find('user_watching').contents[0]) + int(soup.find('user_completed').contents[0]) +\
            int(soup.find('user_onhold').contents[0]) + int(soup.find('user_dropped').contents[0]) +\
            int(soup.find('user_plantowatch').contents[0])

    counter = 0
    master = {}

    def get(urls, index):
        nonlocal master, counter, titles
        if type(urls) is str:
            index = [index]
            urls = [urls]
        for idx, url in enumerate(urls):
            i = index[idx]
            r = requests.get(url, headers={"user-agent": "iMAL-iOS"})
            soup = BeautifulSoup(r.text, "lxml")
            temp = None
            for k in soup.find_all('tr'):
                for j in k.children:
                    if j.name is not None and j.a is not None and j.a.contents != [] and j.small is not None:
                        att = j.attrs
                        if 'width' not in att and 'valign' in att and att['valign'] == 'top':
                            if temp is None:
                                if j.small.contents[0] == 'Main' or j.small.contents[0] == 'Supporting':
                                    temp = j.a.contents[0]
                            else:
                                if j.small.contents[0] == 'Japanese':
                                    if j.a.contents[0] in master:
                                        master[j.a.contents[0]].append((titles[i].string, temp))
                                    else:
                                        master[j.a.contents[0]] = [(titles[i].string, temp)]
                                temp = None

            counter += 1
            sys.stdout.write('\r')
            sys.stdout.write(str(counter) + '/' + str(total_watched))
            sys.stdout.flush()
        return

    urls = []
    indexes = []
    for i in range(len(titles)):
        urls += ['http://myanimelist.net/anime/' + str(ids[i].contents[0]) + '/' +\
                titles[i].string.replace(' ', '_') + '/characters']
        indexes += [i]

    threads = []
    index = split(indexes, 15)
    for idx, group in enumerate(split(urls, 15)):
        t = Thread(target=get, args=(group, index[idx],))
        t.start()
        threads += [t]

    for t in threads:
        t.join()

    sys.stdout.write('\r')
    display(master, f)

def display(dict, f):
    f = sys.stdout
    if f == 'y' or f == 'Y':
        f = open('voice_actor_cross_reference.txt', 'w')
    for key in dict:
        print(key, file=f)
        for j in dict[key]:
            print('    ' + j[0] + ' - ' + j[1], file=f)
    f.close()
if __name__ == "__main__":
    main()
