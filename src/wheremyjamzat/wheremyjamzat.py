#!/usr/bin/env python

"""wheremyjamzat.py: Get those jamz"""


__author__    = "Paul Pietkiewicz"
__copyright__ = "Copyright 2012, Paul Pietkiewicz"
__email__     = "pawel.pietkiewicz@acm.org"
__version__   = '0.888'

import sys
import argparse
import os
import datetime

from utils import get_directory_name, write_playlist, stations, identify_songs
from grooveshark import download_songs

def main():
    """CLI Driver"""
    parser = argparse.ArgumentParser(description='Music downloader and playlist generator', \
                                     prog='wheremyjamzat.py')
    parser.add_argument('station',
        help='Radio station name', choices=stations)
    now = datetime.datetime.now()

    parser.add_argument('-y', help='Year', action="store", dest="year", type=int, choices=xrange(now.year -2, now.year), default=now.year)
    parser.add_argument('-m', help='Month', action="store", dest="month", type=int, choices=xrange(1, 12), default=now.month)
    parser.add_argument('-d', help='Day', action="store", dest="day", type=int, choices=xrange(1, 31), default=now.day)
    parser.add_argument('-n', help='Number of songs to download', action="store", dest="num_songs", type=int, default=-1)

    cli_args = parser.parse_args()
    provided_date = datetime.datetime(year=cli_args.year, month=cli_args.month, day=cli_args.day)
    if provided_date > now:
        raise argparse.ArgumentError('Provided date cannot be in the future')
	if cli_args.num_songs < -1:
		raise argparse.ArgumentError('Invalid number of songs')

    song_list = identify_songs(provided_date, cli_args.station)
    destination_path = os.path.join(os.path.curdir,
                    get_directory_name(cli_args.station, provided_date))

    if cli_args.num_songs != -1 and cli_args.num_songs < len(song_list):
	    song_list = song_list[:cli_args.num_songs]

    downloaded_songs = download_songs(destination_path, song_list)
    playlist_path = write_playlist(os.path.join(destination_path, 'playlist.m3u'),
        downloaded_songs)
    print "Playlist created: %s" % playlist_path
    print "Done!"

if __name__ == "__main__":
    main()
    sys.exit(0)
