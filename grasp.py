# -*- coding: utf-8 -*-
import os  
import cookielib
import urllib2

def get_cookie(filename):
    from cStringIO import StringIO
    from sqlite3 import dbapi2 as sqlite
    con = sqlite.connect(filename)
    cur = con.cursor()
    cur.execute("select host, path, isSecure, expiry, name, value from moz_cookies")
    ftstr = ["FALSE", "TRUE"]
    s = StringIO()
    s.write('# Netscape HTTP Cookie File\n')  
    s.write('# http://www.netscape.com/newsref/std/cookie_spec.html\n')  
    s.write('# This is a generated file!  Do not edit\n')  
    
    for item in cur.fetchall():
        s.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                item[0], ftstr[item[0].startswith('.')], item[1],
                ftstr[item[2]], item[3], item[4], item[5]))  
    # str(int(time.time()) + 3600*24*7)    
    s.seek(0)
    
    cookie_jar = cookielib.MozillaCookieJar()
    cookie_jar._really_load(s, '', True, True)
    return cookie_jar
    
def get_content(url, cookies="ff_cookies"):
    cookiejar = get_cookie(cookies);
    
    #set proxy for fiddler
    #proxy = urllib2.ProxyHandler({'http':'http://proxy01.cd.intel.com:911'})
    #opener = urllib2.build_opener(proxy, urllib2.HTTPCookieProcessor(cookiejar))
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    urllib2.install_opener(opener)
    
    request = urllib2.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1')
    c = urllib2.urlopen(request)
    return c.read()
    