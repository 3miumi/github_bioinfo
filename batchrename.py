#!/usr/bin/python
# -*- coding: utf-8 -*-

import os       # for getting files from directory
import sys      # for accessing command line arguments

# Command line arguments
assert len(sys.argv)<4, "batchrename takes at most 1 command line argument\n"+\
                        "Use: python batchrename.py [folder_name]"

if len(sys.argv) == 1:
    folder_name = "/mnt/data2/FDA/assemblies/lmNew2"    # Looks in 'saves/' folder from 'scripts/' folder
    print ("Use: python batchrename.py [folder_name]")
    print ("Using default path:/mnt/data2/FDA/assemblies/lmNew2")
elif len(sys.argv) == 2:
    folder_name = sys.argv[1]   # First command line argument is folder

# translation table (TODO make better)
in_list  = ['lm_missing_GCAs.txt']
out_list = ['lm_missing_SRRs.txt']

# make sure slash at end of folder name
os.path.join(folder_name, '/mnt/syn1819/FDA/assemblies/lmNew/ncbi_dataset/data/*/')

# get every FNA file in folder
files_list = os.listdir(folder_name)
for f in files_list: # iterate over all files in files_list
    if f.endswith(".fna"): # check if FNA file (optional)
        if f in in_list:
            print (f + ' becomes ' + out_list[in_list.index(f)]) # DEBUG
            os.rename(folder_name+f, folder_name+out_list[in_list.index(f)])