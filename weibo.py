# -*- coding: UTF-8 -*-
import grasp
from bs4 import BeautifulSoup as bs
import time
from urlparse import urljoin, urlsplit
import re
import redis

r = redis.StrictRedis(host='zhf2', port=6379, db=1)

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

def get_users_by_url(userid, url):
	s = None
	try:
		s = grasp.get_content(url)
	except:
		return False

	soup = bs(s)
	tables = soup('table')
	for t in tables:
		link = t.find('a')
		u = link.attrs['href']
		sp = urlsplit(u)
		r.hset(userid, sp.path[1:].strip(), 1)

	return True


def get_followings(userid):
	url = "http://weibo.cn/%s" % (userid)
	s = grasp.get_content(url)
	soup = bs(s)
	tip = soup.find('div', class_='tip2')
	if(tip == None):
		return []

	a = tip.findChildren() 
	num = int(re.search("\d+", a[1].string).group())
	pages = int(num/10)
	if( num%10 > 0):
		pages += 1

	furl = urljoin('http://weibo.cn/', a[1].attrs['href'])


	for i in range(1, pages+1):
		url = furl + '?page=%d' % i
		print url

		# retry 10 times if fails
		for i in range(10):
			if get_users_by_url(userid, url):break
			print url	
        	time.sleep(5) 

		time.sleep(3)
	r.save()
	
def get_followings_recv(current, backup):
	while True:
		length = r.llen(current)
		for i in range(length):
			key = r.lindex(current, i)
			users = r.hkeys(key)
			for u in users:
				get_followings_atom(u)

		tmp = current
		current = backup
		backup = tmp
		r.delete(backup)


def get_followings_atom(userid):
	log = '.log'
	backup = '.backup'

	if(r.zscore(log, userid) > 1):
		return

	r.zadd(log, 1, userid)	# begin
	get_followings(userid)
	r.lpush(backup, userid)
	r.zadd(log, 2, userid)	# end

def recover():
	log = '.log'
	userids = r.zrangebyscore(log, 1, 1)
	for userid in userids:
		get_followings_atom(userid)





def get_all_followings(userids):
	recover()

	current = '.current'
	backup = '.backup'
	for userid in userids:
		get_followings_atom(userid)

	get_followings_recv(current, backup)
