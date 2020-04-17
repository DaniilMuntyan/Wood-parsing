import time
from datetime import timedelta
import requests
from threading import Lock
from threading import Thread
from bs4 import BeautifulSoup

lock = Lock()

path = 'your path'


def set_url_list(name_thr, url_list, a, b):
    print_to('working.txt', name_thr + ". Boundaries " + str(a) + ":" + str(b))
    #s = "First for Thread №" + name_thr
    c = 0
    i = 0
    url_href = ""
    url = ""
    s = ""
    for i in range(a, b):
        try:
            url = "https://timber.fordaq.com/fordaq/A-Z.html?page=" + str(i)
            req = requests.get(url)
            soup = BeautifulSoup(req.content, 'lxml')
            items = soup.find_all('div', class_='company-title')
            c = 0
            activities_list = soup.find_all('dl', class_='m-b-1')
            reply_rate_list = soup.find_all('div', class_='reply-level')
            employees_list = soup.find_all('li', class_='company-employees')
            for temp in items:
                c += 1
                name = ""
                url_href = temp.find('a').get('href')
                # url_list[(i - 1) * 25 + items.index(temp)] = ("https://timber.fordaq.com" + url_href)
                activities = activities_list[c-1].getText()
                reply_rate = reply_rate_list[c-1].getText()
                employees = employees_list[c-1].getText()
                name, number = get_name_number("https://timber.fordaq.com" + url_href)
                d = {'Name': name, 'Activities': activities.replace('\n', '').replace('\t', '').replace('Activities:', ''),
                     'Reply rate': reply_rate, 'Employees': employees.strip(), 'Phone number': number, 'Url': "https://timber.fordaq.com" + url_href}
                s += str(d) + '\n'
            if (i - a) % 10000 == 0 or i == b - 1:
                print_to('companies.txt', s)
                s = ""
        except BaseException as err:
            print_to('log.txt', "{}\n".format(err) + "i = " + str(i) + "; c = " + str(c) + "\n" + "https://timber.fordaq.com" + url_href + '  ' + url)

    return True


def get_name_number(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'lxml')
    number_web = soup.find('a', attrs={'id': 'companyPhoneNumber'})
    if number_web is None:
        all_text = str(soup.extract())
        name = ""
        number = ""
        name_web = soup.find('div', class_='bizcard-identity')
        if name is not None:
            try:
                name = name_web.find('h1', class_='bizcard-company').getText()
            except BaseException:
                name = "None"
        else:
            name = "None"
        i = all_text.find("'tel:")
        k = i
        for temp in all_text[i:]:
            k += 1
            if temp == ';':
                break
            number += temp

        return name, number.replace("'tel:", '').replace("'", '')
    else:
        name = ""
        number = ""
        name = soup.find('h1', attrs={'class': 'company-name'}).getText().replace('\t', '').replace('\n', '').strip()
        number = number_web.get('href').replace('tel:', '')
        return name, number


def print_to(name, text):
    global path
    with lock and open(path + name, 'a') as f:
        f.write(text)
        f.write('\n')


def main():
    global path

    N = 0
    url_list = []
    c = 0
    url = 'https://timber.fordaq.com/fordaq/A-Z.html'
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    resultsNo = int(soup.find('strong', attrs={'class': 'results-no'}).getText())
    if resultsNo % 25 == 0:
        N = resultsNo / 25
    else:
        N = int(resultsNo / 25) + 1

    boundaries = [int(N / 15) * i for i in range(15)]
    boundaries[0] = 1
    boundaries.append(N + 1)
    threads = []

    print_to('working.txt', "Begin\t" + str(resultsNo) + '\t' + str(N) + '\n' + str(boundaries))
    start_time = time.monotonic()
    for i in range(1, len(boundaries)):
        threads.append(Thread(target=set_url_list, args=(str(i), url_list, boundaries[i-1], boundaries[i],)))
        threads[len(threads) - 1].start()
    for i in range(len(threads)):
        if threads[i].isAlive():
            threads[i].join()

    end_time = time.monotonic()
    print_to('time.txt', str(timedelta(seconds=end_time - start_time)))


if __name__ == '__main__':
    main()

