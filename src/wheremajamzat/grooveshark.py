"""grooveshark_downloader.py: mp3 file downloader based on the wonderful educational work of George Stephanos's
							  groove-dl http://github.com/jacktheripper51/groove-dl"""


import httplib
import StringIO
import hashlib
import uuid
import random
import string
import sys
import gzip
import datetime
import os
import subprocess
import time
from ID3 import *
from utils import get_song_length, get_track_name

if sys.version_info[1] >= 6:  import json
else: import simplejson as json

_useragent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
_referer = "http://grooveshark.com/JSQueue.swf?20120220.01"
_token = None

h = {}
h["country"] = {}
h["country"]["CC1"] = "0"
h["country"]["CC2"] = "0"
h["country"]["CC3"] = "0"
h["country"]["CC4"] = "0"
h["country"]["ID"] = "1"
h["privacy"] = 0
h["session"] = None
h["uuid"] = str.upper(str(uuid.uuid4()))


def prepToken(method, secret):
	rnd = (''.join(random.choice(string.hexdigits) for x in range(6))).lower()
	return rnd + hashlib.sha1(method + ":" + _token + secret + rnd).hexdigest()

def getToken():
	global h, _token
	p = {}
	p["parameters"] = {}
	p["parameters"]["secretKey"] = hashlib.md5(h["session"]).hexdigest()
	p["method"] = "getCommunicationToken"
	p["header"] = h
	p["header"]["client"] = "htmlshark"
	p["header"]["clientRevision"] = "20120220"
	conn = httplib.HTTPSConnection("grooveshark.com")
	conn.request("POST", "/more.php", json.JSONEncoder().encode(p), {"User-Agent": _useragent, "Referer": _referer, "Content-Type":"", "Accept-Encoding":"gzip", "Cookie":"PHPSESSID=" + h["session"]})
	_token = json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]
	#print _token

def getResultsFromSearch(query, what="Songs"):
	p = {}
	p["parameters"] = {}
	p["parameters"]["type"] = what
	p["parameters"]["query"] = query
	p["header"] = h
	p["header"]["client"] = "htmlshark"
	p["header"]["clientRevision"] = "20120220"
	p["header"]["token"] = prepToken("getResultsFromSearch", ":jayLikeWater:")
	p["method"] = "getResultsFromSearch"
	conn = httplib.HTTPConnection("grooveshark.com")
	conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p),
			{"User-Agent": _useragent,
			 "Referer":"http://grooveshark.com/",
			 "Content-Type":"application/json",
			 "Accept-Encoding":"gzip",
			 "Cookie":"PHPSESSID=" + h["session"]})
	j = json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())
	#print j
	try:
		return j["result"]["result"]["Songs"]
	except:
		return j["result"]["result"]

def artistGetSongsEx(id, isVerified):
	p = {}
	p["parameters"] = {}
	p["parameters"]["artistID"] = id
	p["parameters"]["isVerifiedOrPopular"] = isVerified
	p["header"] = h
	p["header"]["client"] = "htmlshark"
	p["header"]["clientRevision"] = "20120220"
	p["header"]["token"] = prepToken("artistGetSongsEx", ":jayLikeWater:")
	p["method"] = "artistGetSongsEx"
	conn = httplib.HTTPConnection("grooveshark.com")
	conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), {"User-Agent": _useragent, "Referer": _referer, "Content-Type":"", "Accept-Encoding":"gzip", "Cookie":"PHPSESSID=" + h["session"]})
	return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())

def getStreamKeyFromSongIDEx(id):
	p = {}
	p["parameters"] = {}
	p["parameters"]["mobile"] = "false"
	p["parameters"]["prefetch"] = "false"
	p["parameters"]["songIDs"] = id
	p["parameters"]["country"] = h["country"]
	p["header"] = h
	p["header"]["client"] = "jsqueue"
	p["header"]["clientRevision"] = "20120220.01"
	p["header"]["token"] = prepToken("getStreamKeysFromSongIDs", ":bangersAndMash:")
	p["method"] = "getStreamKeysFromSongIDs"
	conn = httplib.HTTPConnection("grooveshark.com")
	conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), {"User-Agent": _useragent, "Referer": _referer, "Accept-Encoding":"gzip", "Content-Type":"", "Cookie":"PHPSESSID=" + h["session"]})
	j = json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())
	return j

def header_cb(buf):
	global h
	if "PHPSESSID" in buf:
		buf = buf.split(' ')
		h["session"] = buf[1][10:-1]

def init():
	conn = httplib.HTTPConnection("grooveshark.com")
	conn.request("HEAD", "", headers={"User-Agent": _useragent})
	res = conn.getresponse()
	cookie = res.getheader("set-cookie").split(";")
	h["session"] = cookie[0][10:]



def download_songs(download_directory, song_list, aggressive=False):
	songs = []
	init()
	getToken()
	if not aggressive:
		time.sleep(3)
	for song in song_list:
		print "Searching for: %s by %s" % (song['title'], song['artist'])
		s = getResultsFromSearch("%s %s" % (song['title'], song['artist']))
		stream = getStreamKeyFromSongIDEx(s[0]["SongID"])
		for k,v in stream["result"].iteritems():
			stream=v
		title = s[0]["SongName"]
		artist = s[0]["ArtistName"]
		track_path = os.path.join(download_directory, get_track_name(title, artist))
		start_time = datetime.datetime.now()
		if not os.path.exists(track_path):
			wait_flag = True
			wgets =  'wget --user-agent="%s" --referer=%s --post-data=streamKey=%s -O "%s" "http://%s/stream.php"' % (_useragent, _referer, stream["streamKey"], track_path, stream["ip"])
			p = subprocess.Popen(wgets, shell=True)
			p.wait()
			try:
				id3info = ID3(track_path)
				id3info['TITLE'] = title
				id3info['ARTIST'] = artist
				id3info.write()
				print 'ID3 tags written'
			except InvalidTagError, message:
				print "Invalid ID3 tag:", message
		else:
			print 'File %s already exists' % track_path
			wait_flag = False
		if not aggressive and song != song_list[-1]:
			if wait_flag:
				track_length = datetime.timedelta(seconds=get_song_length(track_path))
				end_time = datetime.datetime.now()
				to_wait = track_length - (end_time - start_time)
				to_wait = to_wait.total_seconds() + 2
			if not wait_flag:
				to_wait = random.randrange(5, 12)
			print "Sleeping for %d seconds" % to_wait
			time.sleep(to_wait)
		songs.append({'path': track_path, 'name': title, 'artist': artist})

	return songs
