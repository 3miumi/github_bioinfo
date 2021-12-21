import os
import sys


if len(sys.argv) == 2:
    if not sys.argv[1].endswith("/"):
        folder_name = sys.argv[1]+"/"


# folder_name = "C:/coding/pythonproject/srr/"

# duplicateCheck =  set()
files_list = os.listdir(folder_name)
for f in files_list: # iterate over all files in files_list
    if os.path.isfile(f):
        if f.endswith("contigs.fasta"): # check if FNA file (optional)
            base_filename = f.split('_')[0] +".fasta"
            origin_path = os.path.join(folder_name, f)
            final_path = os.path.join(folder_name, base_filename)
            print (f + ' becomes ' + base_filename) # DEBUG
            os.rename(folder_name+f, final_path)
    

               




