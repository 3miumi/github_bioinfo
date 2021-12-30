#!/usr/bin/python
# -*- coding: utf-8 -*-

import os       # for getting files from directory
import sys      # for accessing command line arguments
import glob

# Command line arguments
# assert len(sys.argv)<4, "batchrename takes at most 1 command line argument\n"+\
#                         "Use: python batchrename.py [folder_name]"

# if len(sys.argv) == 1:
#     folder_name = "/mnt/data2/FDA/assemblies/lmNew2"    # Looks in 'saves/' folder from 'scripts/' folder
#     print ("Use: python batchrename.py [folder_name]")
#     print ("Using default path:/mnt/data2/FDA/assemblies/lmNew2")
# elif len(sys.argv) == 2:
#     folder_name = sys.argv[1]   # First command line argument is folder

# translation table (TODO make better)

def main():

    with open('missing_GCAs.txt') as f:
        in_list  = [line.strip() for line in f]

    with open('missing_SRRs.txt') as f:
        out_list  = [line.strip() for line in f] 
    # print(in_list)
    # print(out_list)

    # make sure slash at end of folder name

    folder_name = os.getcwd()


    # fna_path = os.getcwd()
        
    # get every FNA file in folder
    def check(str):
        with open('missing_GCAs.txt') as f:
            datafile = f.readlines()
        found = False  # This isn't really necessary
        for line in datafile:
            if str in line:
                # found = True # Not necessary
                return True
        return False  # Because you finished the search without finding

    files_list = os.listdir(folder_name)

    for dir in files_list:   
        if dir.startswith('fna'):
            dir = os.path.join(folder_name,dir)
            for f in os.listdir(dir): # iterate over all files in files_list
                if f.endswith(".fna"): # check if FNA file (optional)
                    tempF = f.split('_')[0] +"_"+ f.split('_')[1]
                    
                    if check(tempF):
                        print (tempF + ' becomes ' + out_list[in_list.index(tempF)]) # DEBUG
                        oriPath = os.path.join(dir,f)
                        finalPath = os.path.join(dir,out_list[in_list.index(tempF)]) + ".fna"
                        os.rename(oriPath,finalPath )


if __name__ == "__main__":
     main()
    