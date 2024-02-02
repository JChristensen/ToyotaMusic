#!/home/jack/.venv/bin/python3

import argparse
import logging
import logging.handlers
import mutagen
import os
import pathlib
import re
import sys

def modify_tag(filename):
    """ Need a docstring.
    """
    my_comment = 'Title modified for Toyota'

    filetype = mutagen.File(filename, easy=True)
    if filetype:
        if type(filetype) is mutagen.oggvorbis.OggVorbis:
            logging.debug(f'{filename} is an OggVorbis file.')
            try:
                if filetype['Comment'][0] == my_comment:
                    logging.info(f'{filename} skipped, already has modified title.')
            except Exception as e:
                new_title = make_new_title(filetype['tracknumber'], filetype['title'])
                filetype['title'] = new_title
                filetype['comment'] = my_comment
                filetype.save()
                logging.info(f'{filename} title was modified.')
        elif type(filetype) is mutagen.mp3.EasyMP3:
            logging.debug(f'{filename} is an MP3 file.')
            audio = mutagen.easyid3.ID3(filename)
            cmt = audio.getall('COMM')
            if cmt:
                for c in cmt:
                    if c.text[0] == my_comment:
                        logging.info(f'{filename} skipped, already has modified title.')
            else:
                audio = mutagen.easyid3.EasyID3(filename)
                new_title = make_new_title(audio['tracknumber'], audio['title'])
                audio['title'] = new_title
                audio.RegisterTextKey('comment', 'COMM')
                audio['comment'] = my_comment
                audio.save()
                logging.info(f'{filename} title was modified.')
        else:
            logging.warning(f'{filename} is an unsupported file type {type(filetype)}')
    else:
        logging.warning(f'{filename} may not be an audio file.')

def make_new_title(track, title):
    """ Need a docstring.
    """
    trk = track[0]
    ttl = title[0]
    # track number can be just 'nn' or 'nn/nn' so we use a regex to extract the first number
    p = re.compile('\d+')
    m = p.match(trk)
    trk = m.group(0)
    new_title = str(int(trk)).zfill(2) + ' ' + ttl
    logging.debug(f'Track: {trk} Title: {ttl} New title: {new_title}')
    return new_title

def walk_dir(d):
    """ Need a docstring.
    """
    for child in d.iterdir():
        if child.is_dir():
            walk_dir(child)
        else:
            modify_tag(child)
    return

def main():
    """ Need a docstring.
    """
    # command line arguments
    parser = argparse.ArgumentParser(description='Program to modify music '
        'files for Toyota vehicles so that they play in the correct order.',
        epilog='Many Toyota vehicles use the MP3 title tag rather than the track '
        'number tag to sort music files. This makes it difficult to play the '
        'tracks in the original order. To work around this problem, this '
        'program will modify the title tag by adding the track number to '
        'it as a prefix.')
    parser.add_argument('-v', '--verbose',
        help='print names of the music files as they are processed', action='store_true')
    parser.add_argument('path', help='path to the music files to be modified')
    args = parser.parse_args()

    # create a log file in the same directory as the program
    progpath = os.path.dirname(os.path.realpath(__file__))
    prognamepy = os.path.basename(__file__)     # name.py
    progname = prognamepy.split(sep='.')[0]     # name only
    LOG_FILENAME = f'{progpath}{os.sep}{progname}.log'
    logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

    walk_dir(pathlib.Path(args.path))

if __name__ == '__main__':
    main()
