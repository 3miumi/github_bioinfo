import subprocess,os
from subprocess import PIPE
import shutil
from datetime import date
import unzip_fasta
import batchrename_zm
import shlex



# """Unzip all gz files in the temp/genbank/bacteria"""
# unzip_fasta.main()
# """Change all GCA names to SRR/ERR name: GCA_XXXXXXXX.P0XXXXX.fna -->SRRxxxxxxxx.fna"""
# batchrename_zm.main()



"""Mash sketch all SRR files """

# Generate a new msh folder
workingfoder = os.getcwd()
msh_dir = "msh_" + date.today().isoformat()
msh_Absdir = os.path.join(os.getcwd(),msh_dir)
if not os.path.isdir(msh_Absdir):
    os.mkdir(msh_Absdir)
    

# Find the fna folder and cwd to it
files_list = os.listdir(workingfoder)
for dir in files_list: 
    if dir.startswith('fna'):
        dirpath = os.path.join(workingfoder, dir)
        os.chdir(dirpath)
        break
fnafolder_name = os.getcwd()


# In fna folder, generate mashGenerate.sh for all fna files
with open('mashGenerate.sh', 'w') as file:  
    for f in os.listdir(fnafolder_name): # iterate over all files in files_list
        if f.endswith("fna"): # check if FNA file (optional)\
            tempF = f.split('.')[0]
        # split name GCA_019488765.1_PDT001103426.1_genomic 
            writeIn = "mash sketch -o "+tempF+".msh "+f
            file.write(writeIn)
            file.write('\n')

           
# Start mash sketching and all .msh will be store in fna folder
os.chdir(fnafolder_name)
print ("start")
mashPath = os.path.join(fnafolder_name,'mashGenerate.sh' )
subprocess.call(mashPath, shell=True)
print ("end")


# move all .msh to the msh folder 
for f in os.listdir(fnafolder_name): # iterate over all files in files_list
    if f.endswith("msh"):
        shutil.move(os.path.join(fnafolder_name,f), os.path.join(msh_Absdir, f))








# Mash paste all file
os.chdir(workingfoder)
msh_file = []
for f in os.listdir(msh_Absdir): # iterate over all files in files_list
    if f.endswith("msh"):
        msh_file.append(os.path.join(msh_Absdir, f))
        
        
args = ['mash','paste']
args.append(msh_dir + '_All' )
args += msh_file
print("Starting mash paste")
subprocess.call(args)
print("done")