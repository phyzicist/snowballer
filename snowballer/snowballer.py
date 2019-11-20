#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
snowballer.py Coarsely estimates and visualizes your data creation rate over the past 24 months

Written by Scott Feister 11-15-2019 in reaction to a presentation on data management by Elizabeth Blackwood

Outputs a histogram plot "snowball.png" with an estimate* of MB/month added to your "Documents" folder, over the past two years.

Everything here is written to work with Windows, Mac, or Linux. However, I haven't tested in anything but Windows.

Python dependencies: matplotlib, numpy
Install these dependencies via, e.g. the pip3 package manager:
    pip3 install --user matplotlib numpy

* Caveats:
    - Uses 'date modified' rather than 'date created' -- so if you work with the same files a lot, it will be biased towards saying you've used more data lately
    - People tend to delete their older stuff over time -- and deleted files aren't counted here -- so this will tend to underestimate your data creation rate the further back you go!
"""

import os
import matplotlib
matplotlib.use("Agg") # headless plotting; that is, save plots to image files without any GUI popups
import matplotlib.pyplot as plt
import numpy as np
import datetime

## Define some user settings: root folder and number of months to look back
root = os.path.expanduser(os.path.join("~", "Documents")) # for me in Windows, this is equivalent to root = r"C:\Users\scott\Documents"
nmonths = 24 # Number of months to look backward

## Make a list of all paths to all files in the root folder
# Some path walking code below modified from https://stackoverflow.com/questions/2909975/python-list-directory-subdirectory-and-files
print("Folder: '" + root + "'...")
print("Gathering recursive list of all files...")
fns = [] # A list of all filenames; empty for now.
badnum = 0 # Counter for filenames whose full file path is >255 characters, which causes issues in os.stat() calls that happen with os.path.mtime() calls
for path, subdirs, files in os.walk(root):
    for name in files:
        if (len(path) + len(name)) < 256: # Handle case with Windows and too-long-of-filenames
            fns.append(os.path.join(path, name))
        else:
            badnum += 1
fns = np.array(fns) # Re-define the list of filenames as a NumPy Array of filenames, to facilitate conditional indexing

print("Total files: " + str(fns.shape[0] + badnum))
if badnum > 0:
    print(str(badnum) + " of those are being skipped because the full file path is over 255 characters.")

## Get the POSIX timestamps for all files, rounded to the second
print("Reading file timestamps...")
getmtime = np.vectorize(os.path.getmtime, otypes=[np.int64])
mtimes = getmtime(fns)

## Figure out which files fell in the right date range
ts = datetime.datetime.now().timestamp() # Right now!

sec2month = 1.0/(60*60*24*7*30.42) # Conversion from seconds to months
start = ts - nmonths/sec2month # Look at files modified up to nmonths months ago
end = ts # Look at files modified up until right now.

ct = (mtimes > start) & (mtimes < end) # Boolean NumPy array with same length as file list; True for indices of files last modified in the approved date range, False otherwise
print("Files in date range: " + str(np.sum(ct)))

## For files last modified the right date range, get their file size in Megabytes
print("Getting file sizes...")
getsize= np.vectorize(os.path.getsize)
sizes_MB = getsize(fns[ct]) * 1e-6

## Make and save size-weighted histogram plot
print("Generating plot to estimate monthly data creation rate...")
mtimes_mo = (mtimes[ct] - ts)*sec2month
start_mo = (start - ts)*sec2month
end_mo = (end - ts)*sec2month

fig, ax = plt.subplots()
n, bins, _ = ax.hist(mtimes_mo, bins=nmonths, range=(start_mo, end_mo), weights=sizes_MB)
ax.set_title("Est. Data Creation Rate In '" + root + "'")
ax.set_ylabel("MB per month")
ax.set_xlabel("Month # (0 = now)")
ax.set_xlim([start_mo, end_mo])
plt.tight_layout()
fig.savefig("snowball.png")
plt.close('all')

print("Plot complete! Saved to 'snowball.png'")