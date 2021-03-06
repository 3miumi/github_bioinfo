
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from re import S, T, sub
import sys,os
import shlex,shutil
import subprocess
from matplotlib.pyplot import get

def main(args):
    opts = parse_cmdline_params(args[1:])
    if opts.species == "Salmonella" or opts.species == "salmonella":
        mashCommend = "/mnt/data2/FDA/assemblies/Mash_database_latest/sal/sal_mash_all_011222.msh"
    elif opts.species == "Listeria" or opts.species == "listeria":
        mashCommend ="/mnt/data2/FDA/assemblies/Mash_database_latest/lm/lm_011122_all.msh"
    elif opts.species == "Ecoli" or opts.species == "ecoli":
        mashCommend = "/mnt/data2/FDA/assemblies/Mash_database_latest/ecoli/ecoli_msh_20220114.msh"


    

    f = open("output.tab", "w")
    mash_arg = shlex.split(mashCommend)
    print("Mash distance started:")
    subprocess.call(["mash", "dist", mashCommend, opts.file], stdout=f)

    out = open("topTen.txt", "w")
    sort_args = ['sort', '-gk3','output.tab']
    process_arg = subprocess.Popen(sort_args, stdout=subprocess.PIPE, shell=False)
    # process_arg.wait()
    process_arg2 = subprocess.Popen(['head'], stdin=process_arg.stdout, stdout=out, shell=False)
    process_arg2.communicate()
    


    top = []
    # getTop = False
    with open('topTen.txt') as infile, open('accessions.txt', 'w') as outfile:
        
        for line in infile:
            subline = line.split("\t")[0]
            start = indexOflastdash(subline)
            end = indexofclosing(subline)
            subline = subline[start+1: end]
            top.append(subline)
            outfile.write(subline)
            outfile.write('\n')

    # downloadAccession = "/mnt/data2/FDA/assemblies/lmNew/sra_download.pl accessions.txt --ascp"
    # downloadAccession_args = shlex.split(downloadAccession)


    
    print("Starting download SRR fastq files")
    if opts.ascp:
        subprocess.call(["perl", "/mnt/data2/FDA/assemblies/lmNew/sra_download.pl", "accessions.txt", "--ascp"])
    else:
        subprocess.call(["perl", "/mnt/data2/FDA/assemblies/lmNew/sra_download.pl", "accessions.txt"])
        filelist = os.listdir(os.getcwd())
        for file in filelist:
            if file.endswith(".gz"):
                filename = file.split("_")[0]
                if not os.path.exists(filename):
                    os.mkdir(filename)
                shutil.copy(os.path.join(os.getcwd(), file), filename)
                os.remove(os.path.join(os.getcwd(), file))

    return top

def indexOflastdash(str):
    index = 0
    i = 0
    while i < len(str):
        if str[i] == '/':
            index = i
        i +=1
    return index
# find the index of end of pattern(any char rather than number and letter)


def indexofclosing(str):
    start = indexOflastdash(str)
    index = start +1
    while index < len(str):
        if str[index].isdigit() or str[index].isalpha():
            index +=1             
        else:
            break

    return index


def parse_cmdline_params(arg_list):
    """Parses commandline arguments.
    :param arg_list: Arguments to parse. Default is argv when called from the
    command-line.
    :type arg_list: list.
    """
    #Create instance of ArgumentParser
    options_parser = ArgumentParser(formatter_class=
                                    ArgumentDefaultsHelpFormatter)
    options_parser.add_argument('--species', dest='species', type=str, required=True,
                                help="Known Species for comparison, eg: Salmonella, Listera")

    options_parser.add_argument('--file', dest='file', type=str, required=True,
                                help="name of contigs.fasta, eg: W508975.contigs.fasta")
    options_parser.add_argument('--ascp',
                                help="if ascp commend need to be used(in case Aspera Connect ERROR)", action='store_true')
    
    opts = options_parser.parse_args(args=arg_list)
    return opts


if __name__ == "__main__":
    main(sys.argv)