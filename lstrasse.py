#!/usr/bin/env python

import mechanize, re, lxml.etree, sys, os
from pprint import pprint
from pyquery import PyQuery as pq

def elementToText(element):
    t = element.text or ""
    return t + "".join(map (lxml.etree.tostring, element))

def getEpisodes():
    b = mechanize.Browser()
    b.open("http://www.lindenstrasse.de")
    b.follow_link(url_regex="nonflash")
    b.follow_link(name_regex="LS_Navi")
    b.follow_link(text_regex="blick nach Folge")
    html=b.response().read()

    episodes=[]

    x=pq(html)("td.subnaviheadrot:contains('Folge')").parent().siblings()
    for row in x:
        cols = list(row.iterchildren())
        if len(cols) == 4:
            (link,title,date,_) = cols
            try:
                a = link.iterchildren("a").next()
                href=a.get("href")
                num=a.text
                episodes.append([href,num,title.text,date.text])
            except StopIteration:
                pass
    return episodes[0:9]

def getRTMP(ep):
    b = mechanize.Browser()
    b.open("http://www.lindenstrasse.de")
    b.follow_link(url_regex="nonflash")
    b.follow_link(name_regex="LS_Navi")
    b.follow_link(text_regex="blick nach Folge")
    b.follow_link(text_regex=str(ep))
    b.follow_link(text_regex="Video-Stream")
    html=b.response().read()
    links = re.findall('rtmp://[^&"]*',html)
    link = links[0]

    return link

if len(sys.argv) == 1:
    for ep in getEpisodes():
        print "#%s: %s (%s)" % (ep[1], ep[2], ep[3])
else:
    ep = int(sys.argv[1])
    link = getRTMP(ep)
    f = os.environ["HOME"] + "/Desktop/ls-%s.flv" % ep
    params = ["rtmpdump","-r",link,"--resume","-o",f]
    os.execvp("rtmpdump",params)
