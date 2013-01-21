# -*- coding: UTF-8 -*-
import grasp
from bs4 import BeautifulSoup as bs
import time
from urlparse import urljoin, urlsplit
import re
import redis

class weibo:
	def __init__(self):
		self.db = redis.StrictRedis(host='zhf2', port=6379, db=1)
		self.log = '.log'
		self.scanlist = '.list'

	def add_following(self, userid, following):
		self.db.hset(userid, following, 1)


	def get_users_by_url(self, userid, url):
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
			self.add_following(userid, sp.path[1:].strip())
		return True


	def get_followings(self, userid):
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
			for j in range(10):
				if self.get_users_by_url(userid, url):break
				print url
				time.sleep(5)
			time.sleep(2)
		self.db.save()

	def get_followings_atom(self, userid, recover=False):
		threshold = 1
		if recover: threshold = 2

		if(self.db.zscore(self.log, userid) >= threshold):
			return

		self.db.zadd(self.log, 1, userid)	# being
		self.get_followings(userid)
		self.db.rpush(self.scanlist, userid)
		self.db.zadd(self.log, 2, userid)	# end


	def recover(self):
		unfinished = self.db.zrangebyscore(self.log, 1, 1)
		for userid in unfinished:
			self.get_followings_atom(userid, True)


	def get_all_followings(self, userids):
		self.recover()

		for userid in userids:
			self.get_followings_atom(userid)

		
		index = 0
		while True:
			if(index < self.db.llen(self.scanlist)):
				self.get_followings_atom(self.db.lindex(self.scanlist, index))
