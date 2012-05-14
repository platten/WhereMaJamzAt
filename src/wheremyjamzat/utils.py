"""utils.py: Supplementary utility functions for WhereMyJamz@"""

from urllib import urlopen
import datetime
import re
import subprocess
from bs4 import BeautifulSoup

stations = ['kroq', 'whfs', 'v103']
template = 'http://{station}.radio.com/playlist/{year}/{month}/{day}/'


def identify_songs(datetime_obj=datetime.datetime.now(), station=stations[0]):
	songs = []

	template_dict = {'station': station,
	                 'year': str(datetime_obj.year),
	                 'month': "%02d" % datetime_obj.month,
	                 'day': "%02d" % datetime_obj.day}
	f = urlopen(template.format(**template_dict))
	soup = BeautifulSoup(f)
	tracks = soup.findAll('div', attrs='track_info')
	for track in tracks[9:]:
		title = track.findChild('div', attrs='track_title').text
		artist = track.findChild('div', attrs='track_artist').text
		songs.append({'title': title, 'artist': artist})
	return songs


def get_song_length(track_path):
	song_length = subprocess.check_output('midentify "%s" | grep ID_LENGTH | cut -d"=" -f2' % track_path, shell=True)
	return int(eval(song_length.rstrip()))


def write_playlist(playlist_path, songs):
	fp = open(playlist_path, 'w')
	fp.write('#EXTM3U\n')
	for song in songs:
		fp.write('#EXTINF:%d,%s - %s\n' % (get_song_length(song['path']), song['name'], song['artist']))
	fp.close()
	return playlist_path


def get_track_name(title, artist):
	return re.sub(' ', '_', re.sub('"', '\"', "%s-%s.mp3" % (artist, title)))


def get_directory_name(station, date):
	return "%s-%s" % (station, date.strftime('%m-%d-%y'))