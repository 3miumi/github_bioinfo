import subprocess,os
from subprocess import PIPE
import shutil
from datetime import date
import unzip_fasta
import batchrename_zm
import shlex



"""Unzip all gz files in the temp/genbank/bacteria"""
unzip_fasta.main()
"""Change all GCA names to SRR/ERR name: GCA_XXXXXXXX.P0XXXXX.fna -->SRRxxxxxxxx.fna"""
batchrename_zm.main()



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
            writeIn = "mash sketch -o "+tempF+".msh "+os.path.join(fnafolder_name,f)
            file.write(writeIn)
            file.write('\n')

           
# change mashGenerate.sh location to msh_xx-xx-xxxx
shutil.move(os.path.join(fnafolder_name,'mashGenerate.sh' ), os.path.join(msh_Absdir, 'mashGenerate.sh'))

# Start mash sketching and all .msh will be store in msh folder
os.chdir(msh_Absdir)
print ("start")

mashPath = os.path.join(msh_Absdir,'mashGenerate.sh' )
# permission = "chmod +x "+ mashPath
subprocess.call(["chmod","+x", mashPath])
subprocess.call(mashPath, shell=True)
print ("end")


# # move all .msh to the msh folder 
# for f in os.listdir(fnafolder_name): # iterate over all files in files_list
#     if f.endswith("msh"):
#         shutil.move(os.path.join(fnafolder_name,f), os.path.join(msh_Absdir, f))





# Mash paste all file

os.chdir(workingfoder)
msh_file = []
for f in os.listdir(msh_Absdir):
    if f.endswith("msh"):
        msh_file.append(os.path.join(msh_Absdir,f))


cutoff = 1000 
i = 0 
newMash = msh_dir + "_"+ str(i)+ ".msh"
while i  <= len(msh_file)// cutoff:

    args = ['mash','paste']
    
    args.append(newMash)
    if i > 0:
        oldMash =  msh_dir + "_"+ str(i-1) + ".msh"
        args.append(oldMash)
        args += msh_file[cutoff * i : cutoff*(i+1)]
        print("Starting mash paste: "+ str(i))
        subprocess.call(args)
        print("done")
        i +=1
        os.remove(oldMash)
        newMash = msh_dir + "_"+ str(i) + ".msh"
    else: 
        args += msh_file[cutoff * i : cutoff*(i+1)]
        print("Starting mash paste: "+ str(i))
        subprocess.call(args)
        print("done")
        i +=1
        # os.remove(oldMash)
        newMash = msh_dir + "_"+ str(i) + ".msh"