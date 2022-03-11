
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import sys,os
import shlex,shutil
import subprocess
from datetime import date
import download_SRRaccessions
import referenceChoser


def main(args):
    opts = parse_cmdline_params(args[1:])
    dst = os.getcwd()
    src = []
    src.append(opts.fasta)  
    src.extend(opts.fastq)

    # copy file in synology drive to current directory
    for file in src:
        filename = os.path.basename(file)
        shutil.copyfile(file, os.path.join(dst, filename))

    # get W name
    sampleFolder = os.path.basename(src[0]).split(".")[0]

    # make samples folder
    if not os.path.exists("samples"):
        os.mkdir("samples")

    # move fastq/fasta files into samples
    for file in src:
        shutil.copy(os.path.join(dst, os.path.basename(file)), "samples")
        os.remove(os.path.join(dst, os.path.basename(file)))
   
    # make W folder
    os.chdir("samples")
    if not os.path.exists(sampleFolder):
        os.mkdir(sampleFolder)


    # group fastq files
    for file in src:
        if file.endswith(".gz"):
            shutil.copy(os.path.join(dst, "samples", os.path.basename(file)), sampleFolder)
            os.remove(os.path.join(dst,"samples", os.path.basename(file)))

    # go to upper directory
    os.chdir(dst)
 
    # make reference folder
    if not os.path.exists("reference"):
        os.mkdir("reference")

    samplePath = os.path.join(dst, "samples")

    try:
        os.chdir(samplePath)
    except:
        print("Copy failed.") # debug
        sys.exit()
    
    # download_SRRaccessions.main(['','--species',  opts.species, '--file', opts.fasta])



    # download SRR accesions and get the closest SRR through mash distance
    topSRR = download_SRRaccessions.main(['','--species',  opts.species, '--file', opts.fasta])
    srrArg = ""

    for srr in topSRR:
        srrArg += srr + " "
    os.chdir(dst)
    referencePath= os.path.join(dst,"reference")
    # get reference by SRR
    referencefile = referenceChoser.main(['','--SRR',srrArg, '--folder', referencePath])

    
    """Run CFSAN """
    arg = "cfsan_snp_pipeline run -s samples "
    arg += os.path.join(referencePath,referencefile )
    final_args= shlex.split(arg)
    proc = subprocess.call(final_args)



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
    options_parser.add_argument('--fasta', dest='fasta', type=str, required=True,
                                help="contigs.fasta file")
    options_parser.add_argument('--fastq', dest='fastq', type=str, nargs='+',required=True,
                                help="two fastq files, seperated by space.")
    opts = options_parser.parse_args(args=arg_list)
    return opts

    
if __name__ == "__main__":
    main(sys.argv)