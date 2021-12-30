import unzip_fasta
import batchrename_zm
import subprocess
import os 
# unzip_fasta.main()
# batchrename_zm.main()

path = os.getcwd()
targetDir = os.path.join(path,"fna*")

print ("start")
res = subprocess.Popen(['C:\coding\gitlab_zm\zming_bioinf\make_sketch_all.sh','.'], shell=True, stdout=subprocess.PIPE)
output = res.communicate()[0]
print(output)
# res.stdout.read()  
subprocess.Popen(output, shell=True)
# res.stdout.close() 
print ("end")
