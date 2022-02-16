
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys,os
import shlex
import subprocess
from datetime import date
import second_CFSAN
def main(args):
    opts = parse_cmdline_params(args[1:])
    if opts.species == "Salmonella" or opts.species == "salmonella":
        mashCommend = "/mnt/data2/FDA/assemblies/Mash_database_latest/sal/sal_mash_all_011222.msh"
    elif opts.species == "Listeria" or opts.species == "listeria":
        mashCommend ="/mnt/data2/FDA/assemblies/Mash_database_latest/lm/lm_011122_all.msh"
    elif opts.species == "Ecoli" or opts.species == "ecoli":
        mashCommend = "/mnt/data2/FDA/assemblies/Mash_database_latest/ecoli/ecoli_msh_20220114.msh"

    # get the name of W number
    


  
    topTen = []
    root = os.getcwd()

    orilist = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item))]
    accessionsList = []
    count =  0
    files = opts.file.split(",")
    for file in files:
        w_number = file.split(".")[0]
        start_w_number = indexOflastdash(w_number)

        accessions = "accessions_" + w_number[start_w_number+1:] + ".txt"
        accessionsList.append(accessions)
        # create output_date.tab file for new sample
        output = "output_" + w_number[start_w_number + 1:] + ".tab"
        if not os.path.isfile(output) : 
            f = open(output, "w")
            mash_arg = shlex.split(mashCommend)
            print(w_number[start_w_number+1:] + " Mash distance started:")
            subprocess.call(["mash", "dist", mashCommend, file], stdout=f)
            # create new topTen_date.txt for new sample

        # topten = "topten" + date.today().isoformat() + ".txt"
        # out = open(topten, "w")
        
        sort_args = ['sort', '-gk3', output]
        process_arg = subprocess.Popen(sort_args, stdout=subprocess.PIPE, shell=False)
        # process_arg.wait()
        process_arg2 = subprocess.Popen(['head'], stdin=process_arg.stdout, stdout=subprocess.PIPE, shell=False)
        topTen = process_arg2.stdout.readlines()
        process_arg2.communicate()
        

        
        # orilist = open("accessions.txt", 'r').readlines()
      
        with open(accessions, 'w') as outfile:
            for line in topTen:
                line = line.decode()
                subline = line.split("\t")[0]
                start = indexOflastdash(subline)
                end = indexofclosing(subline)
                subline = subline[start+1: end]
                if subline not in orilist:
                    print(subline)
                    count += 1
                    outfile.write(subline)
                    outfile.write('\n')
                    orilist.append(subline)

    print("Total of " + str(count) + " isolates were added in the list")
    
    ans = input("Do you want to contiune the SNP analysis?[Y/N] ")
    if ans != 'Y' and ans != 'y':
        print(type(ans))
        sys.exit()


    if opts.ascp:
        second_CFSAN.main(['','--file', ','.join(accessionsList),"--ascp"])
    else:
        second_CFSAN.main(['','--file', ','.join(accessionsList)])


def indexOflastdash(str):
    index = -1
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

    