import ftplib
from ftplib import FTP
import os
import sys

# from datetime import datetime

if len(sys.argv) == 3:
    species_name = sys.argv[1]   # First command line argument is folder
    output_folder = sys.argv[2]



Ftp_source_files_path = '/pathogen/Results/'+ species_name
Meta_folder = 'Metadata'

#Connect ftp ncbi FTP site
ftp = ftplib.FTP('ftp.ncbi.nlm.nih.gov')  
ftp.login()
print("connected to remote server : ftp.ncbi.nlm.nih.gov")
print()

def get_matadata_ftp(folder=""):
    contents = ftp.nlst(folder)
    folders = []
    for item in contents:
        if item[-1].isdigit():
            folders.append(item)

    folders.sort(key=lambda x: int(x.split(".")[1]))   

    return folders[len(folders)-1]


# find the path: /pathogen/Results/species_name/PDG00000001.XXXX  /Metadata/
latest_path = get_matadata_ftp(Ftp_source_files_path)
filepath = os.path.join(latest_path,Meta_folder).replace("\\","/")
print("Find the latest folder in NCBI site:"+ filepath)



def downloadFiles(path):
#path are str of the form "/dir/folder/something/"
#path should be the abs path to the root FOLDER of the file tree to download
    try:
    #     # change into "path directory"
        ftp.cwd(path)

    #     #clone path to destination
       
        print ("Download to current directory: " + output_folder)
    except ftplib.error_perm:
        # invalid entry (ensure input form: "/dir/folder/something/")
        print ("error: could not change to "+path)
        sys.exit("ending session")


    #list children:
    filelist=ftp.nlst()

    for file in filelist:
        try:
            #this will check if file is folder:
            ftp.cwd(path+file+"/")
            #if so, explore it:
            downloadFiles(path+file+"/")
        except ftplib.error_perm:
            #not a folder with accessible content
            #download & return
            if file.endswith(".tsv"):
                #possibly need a permission exception catch:
                ftp.retrbinary("RETR "+file, open(os.path.join(output_folder,file).replace("\\","/"),"wb").write)
                print (file + " downloaded")
    return

source = filepath
downloadFiles(source)