# About

The goal of this script is to identify duplicates in the filesystem.


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


