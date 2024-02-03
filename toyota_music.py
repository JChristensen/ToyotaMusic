#!/home/jack/.venv/bin/python3

import argparse
import logging
import logging.handlers
import mutagen
import os
import pathlib
import re
import sys
import time

class Toyota_Tags:
    """A class to do bulk modification of title tags in audio files
    so that Toyota vehicles can sort them in the proper order.
    MP3 and OggVorbis audio files can be processed.
    """

    def __init__(self, verbose=False, quiet=False):
        """Initialize attributes."""
        self.logger = logging.getLogger(__name__)
        self.TOYOTA_COMMENT = 'Title modified for Toyota'
        self.verbose = verbose
        self.quiet = quiet
        self.files_processed = 0
        self.files_modified = 0
        self.files_skipped = 0
        self.files_unsupported = 0
        self.files_not_audio = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.dir_level = 0

    def modify_tag(self, filename):
        """ Modify the title tag on the given audio file, and add a comment
        tag to indicate that the title has been modified.
        Skip modifying any files that already have the comment.
        """
        self.files_processed += 1
        filetype = mutagen.File(filename, easy=True)
        if filetype:
            if type(filetype) is mutagen.oggvorbis.OggVorbis:
                self.logger.debug(f'{filename} is an OggVorbis file.')
                try:
                    if filetype['Comment'][0] == self.TOYOTA_COMMENT:
                        self.files_skipped += 1
                        self.logger.info(f'{filename} skipped, already has modified title.')
                        if self.verbose: print(f'Skipped: {filename}')
                except Exception as e:
                    new_title = self.make_new_title(filetype['tracknumber'], filetype['title'])
                    filetype['title'] = new_title
                    filetype['comment'] = self.TOYOTA_COMMENT
                    filetype.save()
                    self.files_modified += 1
                    self.logger.info(f'{filename} title was modified.')
                    if self.verbose: print(f'Modified: {filename}')
            elif type(filetype) is mutagen.mp3.EasyMP3:
                self.logger.debug(f'{filename} is an MP3 file.')
                audio = mutagen.easyid3.ID3(filename)
                cmt = audio.getall('COMM')
                if cmt:
                    for c in cmt:
                        if c.text[0] == self.TOYOTA_COMMENT:
                            self.files_skipped += 1
                            self.logger.info(f'{filename} skipped, already has modified title.')
                            if self.verbose: print(f'Skipped: {filename}')
                else:
                    audio = mutagen.easyid3.EasyID3(filename)
                    new_title = self.make_new_title(audio['tracknumber'], audio['title'])
                    audio['title'] = new_title
                    audio.RegisterTextKey('comment', 'COMM')
                    audio['comment'] = self.TOYOTA_COMMENT
                    audio.save()
                    self.files_modified += 1
                    self.logger.info(f'{filename} title was modified.')
                    if self.verbose: print(f'Modified: {filename}')
            else:
                self.files_unsupported += 1
                self.logger.warning(f'{filename} is an unsupported file type {type(filetype)}')
                if self.verbose: print(f'Unsupported file: {filename}')
        else:
            self.files_not_audio += 1
            self.logger.warning(f'{filename} may not be an audio file.')
            if self.verbose: print(f'Not an audio file: {filename}')

    def make_new_title(self, track, title):
        """ Need a docstring.
        """
        trk = track[0]
        ttl = title[0]
        # track number can be just 'nn' or 'nn/nn' so we use a regex to extract the first number
        p = re.compile('\d+')
        m = p.match(trk)
        trk = m.group(0)
        new_title = str(int(trk)).zfill(2) + ' ' + ttl
        self.logger.debug(f'Track: {trk} Title: {ttl} New title: {new_title}')
        return new_title

    def modify_tags(self, d, level=0):
        """ Recurse through the given directory, attempt to modify
        the title tag on each file.
        """
        if level == 0: self.start_time = time.time_ns()
        for child in d.iterdir():
            if child.is_dir():
                self.modify_tags(child, level+1)
            else:
                self.modify_tag(child)
        if level == 0:
            self.elapsed_time = (time.time_ns() - self.start_time) / 1e9
            self.print_stats()
        return

    def print_stats(self):
        """Print the number of files processed, etc."""
        if not self.quiet:
            print(f'---- End run, elapsed time {self.elapsed_time} seconds.')
            print(f'Files processed:         {self.files_processed}')
            print(f'Audio files modified:    {self.files_modified}')
            print(f'Audio files skipped:     {self.files_skipped}')
            print(f'Unsupported audio files: {self.files_unsupported}')
            print(f'Non-audio files:         {self.files_not_audio}')

def main():
    """ Need a docstring.
    """
    # command line arguments
    parser = argparse.ArgumentParser(description='Program to modify audio '
        'files for Toyota vehicles so that they play in the correct order.',
        epilog='Many Toyota vehicles use the title tag rather than the track '
        'number tag to sort audio files. This makes it difficult to play '
        'tracks in the original order. To work around this problem, this '
        'program will modify the title tag by adding the track number to '
        'it as a prefix. \n \n '
        'This program will recurse through the directory given by "path" '
        'and process all audio files under it.')
    opt_group = parser.add_mutually_exclusive_group()
    opt_group.add_argument('-v', '--verbose',
        help='print names of the audio files as they are processed', action='store_true')
    opt_group.add_argument('-q', '--quiet',
        help='run without printing any output, e.g. stats for files processed', action='store_true')
    parser.add_argument('path', help='directory containing the audio files to be modified')
    args = parser.parse_args()

    # create a log file in the same directory as the program
    progpath = os.path.dirname(os.path.realpath(__file__))
    prognamepy = os.path.basename(__file__)     # name.py
    progname = prognamepy.split(sep='.')[0]     # name only
    LOG_FILENAME = f'{progpath}{os.sep}{progname}.log'
    have_previous_logfile = pathlib.Path(LOG_FILENAME).exists()
    logger = logging.getLogger(__name__)
    #logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=4)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
                
    if have_previous_logfile: handler.doRollover()
    tags = Toyota_Tags(verbose=args.verbose, quiet=args.quiet)
    tags.modify_tags(pathlib.Path(args.path))

if __name__ == '__main__':
    main()
