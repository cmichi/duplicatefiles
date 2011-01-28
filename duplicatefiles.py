#!/usr/bin/env python
#
# NAME
# 	duplicatefiles - a script to check if there are duplicate files in the folder
#
# OPTIONS
#	-l, --loglevel 
#		debug, info, warning, error, fatal or spam (very verbose)	
#		Default: info
#
#	-t, --treshold
#		The minimum file size a file has to have, to get compared (in bytes!).
#		Default: 1024 bytes 
#
#	-d, --database
#		The database to use.
#		Default: /tmp/dupfdb.<randomint>
#
#	-c
#		Outputs total count and estimated file size that could be saved by deleting duplicates.
#
# EXAMPLE
#	Default values
#		$ python duplicatefiles.py ./foo
#
#	Output only errors
#		$ python duplicatefiles.py -l=error ./foo
#
# INFO
#	Works with python 2.6.1
#

import os
import sys
import hashlib
import logging
import random
import sqlite3


# init logging
level = logging.INFO

# very verbose output? outputs processing of every file
SPAM = False

# a database file to store the huge amount of data that will be gathered
database = "/tmp/dupfdb.%d" % random.randint(0,2**32)

# files that are smaller than the threshold will be ignored
threshold = 1024

outputTotal = False

loglevel = {"debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "fatal":logging.FATAL,
            "spam":logging.DEBUG
}

# parse arguments
for i in range(len(sys.argv)):
    if sys.argv[i] == "-l" or sys.argv[i] == "--loglevel":
        level = loglevel[sys.argv[i+1].lower()]
    if sys.argv[i].lower() == "spam":
        SPAM = True
    if sys.argv[i] == "-t" or sys.argv[i] == "--treshold":
        threshold = int(sys.argv[i+1])
    if sys.argv[i] == "-d" or sys.argv[i] == "--database":
        database = sys.argv[i+1]
    if sys.argv[i] == "-c":
        outputTotal = True

logging.basicConfig(level=level)

dir = sys.argv[len(sys.argv) - 1]

def spam(msg):
    if SPAM:
        logging.debug("SPAM:%s" % msg)

def hash_file(path):
    "returns hashsum as string"
    spam("hashing %s" % path)
    f = open(path)
    md5 = hashlib.md5()
    while True:
        # do NOT load the whole file into memory
        # whole files in memory aren't kewl
        byte = f.read(10*1024)
        if not byte:
            break
        md5.update(byte)
    f.close()
    return md5.hexdigest()


# connect to the database
dbconnection = sqlite3.connect(database)
db = dbconnection.cursor()

# create tables for the data
db.execute("CREATE TABLE files (size INTEGER, path TEXT)")
db.execute("CREATE TABLE same (tag TEXT, path TEXT)")

logging.debug("threshold is %d" % threshold)

# first collect all files that aren't directories or symlinks
logging.info("searching for files in directory ('%s')" % dir)

# don't store this in the database. hopefully we won't have so many directories
# that the programm will run out of memory
dirs = [dir]
filecounter = 0


while len(dirs) > 0:
    curdir = dirs.pop()

    for f in os.listdir(curdir):
        f = curdir + os.sep + f
        if os.path.islink(f):
            # don't bother us with links *grrr*
            continue

        if os.path.isfile(f):
            size = os.path.getsize(f)
            if size <= threshold:
                spam("ignored %s" % f)
                continue
            try:
                db.execute("INSERT INTO files VALUES(?, ?)", (size, unicode(f, "UTF-8")))
            except UnicodeDecodeError:
                logging.error("%s caused a UnicodeDecodeError. Ignoring and moving on." % f)

            filecounter += 1
            spam("found %d files" % filecounter)

            if filecounter%10000 == 0:
                dbconnection.commit()
                logging.debug("found %d files" % filecounter)
            # end debug
        elif os.path.isdir(f):
            dirs.append(f)
        # else ignore (if neither file nor directory, e.g. symlink)

dbconnection.commit()

logging.info("found %d files bigger than %d bytes" % (filecounter, threshold))
logging.info("starting hashing of files")

# replaced by table same
count = 0
cur = dbconnection.cursor()
cur.execute("SELECT DISTINCT size FROM files")

while True:
    row = cur.fetchone()
    if not row:
        break

    # only files of the same size can be identical
    size = row[0]
    db.execute("SELECT * FROM files WHERE size=%d" % size)
    entries = db.fetchall()

    if len(entries) < 2:
        continue
    for entry in entries:
        db.execute("INSERT INTO same VALUES (?, ?)",
                (unicode("%d:%s" % (size, hash_file(entry[1])), "UTF-8"), entry[1]))
        count += 1
        spam("processed %d files" % count)
        if count%1000 == 0:
            logging.debug("processed %d files" % count)
            dbconnection.commit()

dbconnection.commit()

logging.info("done hashing")
logging.info("looking for duplicates")

db.execute("SELECT DISTINCT tag FROM same AS s WHERE (SELECT COUNT(tag) FROM same as s2 where s2.tag=s.tag)>1")
tags = db.fetchall()

countTotal = 0
for tag in tags:
    db.execute("SELECT path FROM same WHERE tag='%s'" % tag[0])
    print("these files are the same: ")
    for path in db:
        print("%s" % path[0])
        countTotal += 1
    print("")


if outputTotal and len(tags) > 0:
    duplicateSpace = 0
    for tag in tags:
        db.execute("SELECT path FROM same WHERE tag='%s'" % tag[0])
        firstRun = True
        paths = db.fetchall()
        for path in paths:
            db.execute("SELECT size FROM files WHERE path='%s'" % path)

            if firstRun == True: 
                firstRun = False
            else: 
                duplicateSpace += db.fetchone()[0]

    print "\n-------------------------------"
    print "Duplicate files, total: ", countTotal
    print "Estimated space freed after deleting duplicates: ca. %s MiB" % (duplicateSpace / 1024 / 1024)


# delete database file
os.remove(database)

logging.info("END OF LINE")
