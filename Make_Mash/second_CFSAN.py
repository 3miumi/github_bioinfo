
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys,os
import shlex
import subprocess
from subprocess import CalledProcessError, PIPE
from datetime import date
def main(args):
    opts = parse_cmdline_params(args[1:])

    # downloadAccession = "/mnt/data2/FDA/assemblies/lmNew/sra_download.pl accessions.txt --ascp"
    # downloadAccession_args = shlex.split(downloadAccession)
    print("Starting download SRR fastq files")

    filesize = os.path.getsize(opts.file)

    if filesize != 0:
        if opts.ascp:
            try:

                p = subprocess.run(["perl", "/mnt/data2/FDA/assemblies/lmNew/sra_download.pl", opts.file, "--ascp"])
            except CalledProcessError as err:
                print("Error ocurred: " + err.stderr)
                sys.exit()
        else:
            try:

                p = subprocess.run(["perl", "/mnt/data2/FDA/assemblies/lmNew/sra_download.pl", opts.file])
                organzied = "for i in $(awk -F \"_ \" '{print $1}' <(ls *.gz) | sort | uniq); do mkdir $i; mv $i*.gz $i/.; done"
                organzied_arg= shlex.split(organzied) 
                subprocess.call(organzied_arg, shell = True)
                
            except CalledProcessError as err:
                print("Error ocurred: " + err.stderr)
                sys.exit()
                # perl_arg = "perl /mnt/data2/FDA/assemblies/lmNew/sra_download.pl accessions.txt --ascp"
            
    else:
        print("No new accesions added.")
        print("SNP analysis starting...")
    
    print(os.getcwd())
    path_parent = os.path.dirname(os.getcwd())
    os.chdir(path_parent)
    print(os.getcwd())
    ref_dir = os.path.join(os.getcwd(), "reference")
    files_list = os.listdir(ref_dir)


    ref_name = ""
    for file in files_list:
        if file.endswith(".fna"):
            ref_name = file
            break
    

    new_dir = "SNP" +  date.today().isoformat()
    new_path = os.path.join(os.getcwd(), new_dir)
    if not os.path.isdir(new_path):
        os.mkdir(new_path)
    
    
    sample_path = os.path.join(os.getcwd(),"samples")
    ref_path = os.path.join(ref_dir, ref_name)
    os.chdir(new_path)
    args =  "cfsan_snp_pipeline run -s " + " " + sample_path +" "+ ref_path
    final_args= shlex.split(args) 
    subprocess.call(final_args)



    lines =  open("snp_distance_matrix.tsv", 'r').readlines()
    num = len(lines[0].split())
    lines[0] = str(num) + "\n"
    file = open("snp_distance_matrix.tsv", 'w')
    for line in lines:
        file.write(line)
    file.close()

    

    tree =  "fastme -i snp_distance_matrix.tsv" 
    tree_args= shlex.split(tree) 
    subprocess.call(tree_args)

def parse_cmdline_params(arg_list):
    """Parses commandline arguments.
    :param arg_list: Arguments to parse. Default is argv when called from the
    command-line.
    :type arg_list: list.
    """
    #Create instance of ArgumentParser
    options_parser = ArgumentParser(formatter_class=
                                    ArgumentDefaultsHelpFormatter)
    options_parser.add_argument('--file', dest='file', type=str, required=True,
                                help="accessions, eg: accessions.txt")

    options_parser.add_argument('--ascp',
                                help="if ascp commend need to be used(in case Aspera Connect ERROR)", action='store_true')
    
    
    opts = options_parser.parse_args(args=arg_list)
    return opts


if __name__ == "__main__":
    main(sys.argv)