#!/usr/bin/python3
import sys
import pprint
import requests
import lxml
import time
from bs4 import BeautifulSoup
from threading import Thread


def split(a, n):
    le = len(a)
    if n > le:
        n = le
    k, m = int(le / n), le % n
    sliced = []
    if k > 0:
        for i in range(n):
            sliced += [a[i * k:(i + 1) * k]]
    if m > 0:
        sliced += [a[-m:]]
    return sliced


def main():
    usr = 's0hvaperuna'#input("MAL username: ")
    f = 'n'#input("Save to file (y/n): ")
    s = 'a'#input("Filter\na(all), w(watching), c(completed), o(onhold), d(dropped), p(plan to watch)\nYou can combine different categories e.g. wd would get all from watching and dropped\n")

    r = requests.get('http://myanimelist.net/malappinfo.php?u=' + str(usr) + '&status=all&type=anime',
                     headers={"user-agent": "iMAL-iOS"})

    soup = BeautifulSoup(r.text, "lxml-xml")

    if 'a' in s:
        titles = soup.find_all('series_title')
        ids = soup.find_all('series_animedb_id')
        total_watched = int(soup.find('user_watching').contents[0]) + int(soup.find('user_completed').contents[0]) + \
                        int(soup.find('user_onhold').contents[0]) + int(soup.find('user_dropped').contents[0]) + \
                        int(soup.find('user_plantowatch').contents[0])
    else:
        status = []
        titles = []
        ids = []
        total_watched = 0
        if 'w' in s:
            status += [1]
            total_watched += int(soup.find('user_watching').contents[0])
        if 'c' in s:
            status += [2]
            total_watched += int(soup.find('user_completed').contents[0])
        if 'o' in s:
            status += [3]
            total_watched += int(soup.find('user_onhold').contents[0])
        if 'd' in s:
            status += [4]
            total_watched += int(soup.find('user_dropped').contents[0])
        if 'p' in s:
            status += [6]
            total_watched += int(soup.find('user_plantowatch').contents[0])

        all_titles = soup.find_all('anime')
        for title in all_titles:
            if int(title.find('my_status').contents[0]) in status:
                titles += [title.find('series_title')]
                ids += [title.find('series_animedb_id')]
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
    thread = 15 # Max amount of full sized threads. Usually there will be one more smaller thread
    index = split(indexes, thread)
    t1 = time.time()
    for idx, group in enumerate(split(urls, thread)):
        t = Thread(target=get, args=(group, index[idx],))
        t.start()
        threads += [t]
    for t in threads:
        t.join()
    sys.stdout.write('\r')
    print('\n', time.time() - t1)
    display(master, f)


def display(dict, f):
    if f == 'y' or f == 'Y':
        f = open('voice_actor_cross_reference.txt', 'w')
    else:
        f = sys.stdout
    for key in dict:
        print(key, file=f)
        for j in dict[key]:
            print('    ' + j[0] + ' - ' + j[1], file=f)


if __name__ == "__main__":
    t = time.time()
    main()
    print('Total time: ', time.time() - t)