# About

The goal of this script is to identify duplicates in the filesystem.

OPTIONS
  7 #   -l, --loglevel 
  8 #       debug, info, warning, error, fatal or spam (very verbose)   
  9 #       Default: info
 10 #
 11 #   -t, --treshold
 12 #       The minimum file size a file has to have, to get compared (in bytes!).
 13 #       Default: 1024 bytes 
 14 #
 15 #   -d, --database
 16 #       The database to use.
 17 #       Default: /tmp/dupfdb.<randomint>
 18 #
 19 #   -c
 20 #       Outputs total count and estimated file size that could be saved by deleting duplicates.
 21 #
 22 # EXAMPLE
 23 #   Default values
 24 #       $ python duplicatefiles.py ./foo
 25 #
 26 #   Only output errors
 27 #       $ python duplicatefiles.py -l=error ./foo
 28 #
 29 # INFO
 30 #   Works with python 2.6.1

## Usage
	
Output only errors

	$ python duplicatefiles.py -l=error ./foo


The call

	$ python duplicatefiles.py -l=error -c ./foo

generates the output
	these files are the same: 
	.//music/foo/bar.mp3
	.//music/bar/foo.mp3

	-------------------------------
	Duplicate files, total:  15
	Estimated space freed after deleting duplicates: ca. 40 MiB


