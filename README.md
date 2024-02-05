# ToyotaMusic
#### A program to work around a bug in Toyota infotainment systems.
https://github.com/JChristensen/ToyotaMusic  
README file  

## License
ToyotaMusic program Copyright (C) 2024 Jack Christensen GNU GPL v3.0

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License v3.0 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/gpl.html>

## Overview
This is a command-line Python program to modify audio files on a USB stick so that Toyota vehicles will play them in the correct order.

Many Toyota vehicles use the title tag rather than the track number tag
to sort audio files played from a USB stick. This makes it difficult to
play tracks in the original order ([for](https://www.toyotanation.com/threads/mp3-files-not-playing-in-correct-order-from-usb-drive.1655674/) [example](https://www.toyotaownersclub.com/forums/topic/192692-2020-rav4-usb-track-order/).)

To work around this problem, this program will modify the title tag by
adding the track number to it as a prefix.

The program will recurse through the directory given and process
all audio files under it. Currently the program can process MP3 and
OggVorbis audio files. A log file is written each time the program
is run, noting any failures and other detail information. Log files
for the last three runs are kept; older logs are automatically deleted.

## Prerequisites
This program uses [Mutagen](https://mutagen.readthedocs.io/), a Python multimedia tagging library.

Other libraries used by this program are included in the Python Standard Library.

## Running the program
It is not recommended to run the program on your original music files. First, copy the desired files to a USB stick, then run the program on the USB stick.

Music files modified by this program have been tested on:
- 2022 RAV4
- 2023 Tacoma
