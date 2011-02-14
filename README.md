# About

The goal of this script is to identify duplicates in the filesystem.
In my case I used it to sanatize my 140 GB media folder from duplicated mp3 files and saved about 800 MB.
Using the flag `-s` the script keeps one occurence of the file, deletes duplicates and sets hardlinks.

iTunes had no problems with the mediatek after I executed the script.


## Usage
	
The call 

	$ python duplicatefiles.py -s /foo/

keeps one occurence of the file and deletes the duplicates. 
Then hardlinks which point to the first occurence of the file are generated for the duplicates.

---------------------------------------

Output only errors:

	$ python duplicatefiles.py -l=error ./foo

---------------------------------------

The call

	$ python duplicatefiles.py -l=error -c ./foo

generates the output
	these files are the same: 
	.//music/foo/bar.mp3
	.//music/bar/foo.mp3

	-------------------------------
	Duplicate files, total:  15
	Estimated space freed after deleting duplicates: ca. 40 MiB


## Problems & Solutions
`OSError: [Errno 1] Operation not permitted`
If you use a mac this is possibly related to locked files.

Run `chflags -R nouchg *` on the folder you are trying to sanatize to recursively unlock all files.


## ToDo

 * File processing: Check if file is locked, if true try to unlock it
 * Add flag: Just process filetype *.jpg, for example
 * Replace the syscalls with plattform-independent python methods
