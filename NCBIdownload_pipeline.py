from os import environ
import shlex, subprocess

print("Please enter species name:")
name1 = str(input())
print("Please enter existing folder:")
name2 = str(input())



# environ["BAR1"] = name1
# environ["BAR2"] = name2
import download_missing
# argument = "--species "+ name1 + "  --folders " + name2 
# print(argument)

download_missing.main(['','--species', name1, '--folders', name2 ])


NCBI_download= "ncbi-genome-download -F fasta -s genbank -A missing_GCAs.txt --human-readable -o temp all"
args = shlex.split(NCBI_download)
print(args)
p = subprocess.Popen(args)



