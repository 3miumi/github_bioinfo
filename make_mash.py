import unzip_fasta
import batchrename_zm
import subprocess
import os 


# unzip all files and copy it in to folder fna_xx-xx-xxxx
unzip_fasta.main()
# change all fna name in fna_xx-xx-xxxx from GCA to SRR
batchrename_zm.main()


# run mash sketch
path = os.getcwd()

print ("start")
res = subprocess.Popen(['C:\coding\gitlab_zm\zming_bioinf\make_sketch_all.sh','.'], shell=True, stdout=subprocess.PIPE)
output = res.communicate()[0]
print(output)
# res.stdout.read()  
subprocess.Popen(output, shell=True)
# res.stdout.close() 
print ("end")

