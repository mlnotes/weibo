# -*- coding: UTF-8 -*-
import grasp
from bs4 import BeautifulSoup as bs
import time

def get_status_by_page(page, id, fh):
    url = "http://weibo.cn/%s?page=%s" % (id, page)
    print url
    s = grasp.get_content(url)
    soup = bs(s)
    ctt = soup.find_all('span', class_='ctt')
    if(len(ctt) == 0): return False
    
    for status in ctt:
        fh.write("%s\n" % (status.contents[0].encode("utf8")))
    return True
    
def get_status(id, file, pages=None):
    f = open(file, 'w')
    page = 1
    while(get_status_by_page(page, id, f)):
        if pages != None and pages == page:
            break
    
        page += 1
        time.sleep(5)
    f.close()