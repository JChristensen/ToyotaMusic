#!/usr/bin/python3
# Program to modify audio files on a USB stick so that Toyota vehicles
# will play them in the correct order.
# https://github.com/JChristensen/Toyota_Music
# Copyright (C) 2024 by Jack Christensen and licensed under
# GNU GPL v3.0, https://www.gnu.org/licenses/gpl.html

import argparse
import logging
import logging.handlers
import mutagen          # https://mutagen.readthedocs.io/
import os
import pathlib
import re
import sys
import time

class Toyota_Tags:
    """A class to do bulk modification of title tags in audio files
    so that Toyota vehicles will sort them in the proper order.
    MP3 and OggVorbis audio files can be processed.
    """

    def __init__(self, verbose=False, quiet=False):
        """Initialize attributes and initiate logging."""
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

        # create a log file in the same directory as the program
        progpath = os.path.dirname(os.path.realpath(__file__))
        prognamepy = os.path.basename(__file__)     # name.py
        progname = prognamepy.split(sep='.')[0]     # name only
        LOG_FILENAME = f'{progpath}{os.sep}{progname}.log'
        # check for an existing log file. if it exists, we force a rollover below.
        have_previous_logfile = pathlib.Path(LOG_FILENAME).exists()

        self.logger = logging.getLogger(progname)
        handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=2)
        self.logger.addHandler(handler)
        formatter = logging.Formatter(fmt='%(levelname)s:%(message)s')
        handler.setFormatter(formatter)
        self.logger.setLevel(logging.DEBUG)
        if have_previous_logfile: handler.doRollover()

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
        """ Given track and title, return a new title that is prefixed
        with the track number.
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
        finish_msg = \
            f'End run, elapsed time {self.elapsed_time:.3f} seconds.\n' \
            f'Files processed:         {self.files_processed}\n' \
            f'Audio files modified:    {self.files_modified}\n' \
            f'Audio files skipped:     {self.files_skipped}\n' \
            f'Unsupported audio files: {self.files_unsupported}\n' \
            f'Non-audio files:         {self.files_not_audio}'
        self.logger.info(finish_msg)
        if not self.quiet: print(finish_msg)

def main():
    """ Program to modify audio files on a USB stick so that Toyota vehicles
    will play them in the correct order.
    """
    # command line arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=
            'Program to modify audio files so that Toyota vehicles will play them\n'
            'in the correct order from a USB stick.',
        epilog=
            'Many Toyota vehicles use the title tag rather than the track number tag\n'
            'to sort audio files played from a USB stick. This makes it difficult to\n'
            'play tracks in the original order.\n\n'
            'To work around this problem, this program will modify the title tag by\n'
            'adding the track number to it as a prefix.\n\n'
            'The program will recurse through the directory given by "path" and process\n'
            'all audio files under it. Currently the program can process MP3 and\n'
            'OggVorbis audio files. A log file is written each time the program\n'
            'is run, noting any failures and other detail information. Log files\n'
            'for the last three runs are kept; older logs are automatically deleted.')
    opt_group = parser.add_mutually_exclusive_group()
    opt_group.add_argument('-v', '--verbose',
        help='print names of the audio files as they are processed', action='store_true')
    opt_group.add_argument('-q', '--quiet',
        help='run without printing any output, e.g. stats for files processed', action='store_true')
    parser.add_argument('path', help='directory containing the audio files to be modified')
    args = parser.parse_args()

    tags = Toyota_Tags(verbose=args.verbose, quiet=args.quiet)
    tags.modify_tags(pathlib.Path(args.path))

if __name__ == '__main__':
    main()
