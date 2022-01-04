from os import environ
import shlex, subprocess
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys,os
import download_missing

# print("Please enter species name:")
# name1 = str(input())
# print("Please enter existing folder:")
# name2 = str(input())

def main(args):
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
                                    help="Metadata of Species, eg: Salmonella, Listera", default=environ.get("BAR1"))
        options_parser.add_argument('--folders', dest='folders', type=str, required=True,
                                    help="Genome assembly fasta folders (if multiple separate with comma).", default=environ.get("BAR2"))
        opts = options_parser.parse_args(args=arg_list)
        return opts

    opts = parse_cmdline_params(args[1:])


    download_missing.main(['','--species',  opts.species, '--folders', opts.folders])
    



    # Split missing_GCAs.txt into mutiple small txt by 1000 lines
    lines_per_file = 1000
    smallfile = None
    with open('missing_GCAs.txt') as bigfile:
        for lineno, line in enumerate(bigfile):
            if lineno % lines_per_file == 0:
                if smallfile:
                    smallfile.close()
                small_filename = 'missing_GCAs_{}.txt'.format(lineno + lines_per_file)
                smallfile = open(small_filename, "w")
            smallfile.write(line)
        if smallfile:
            smallfile.close()

    workingfoder = os.getcwd()
    GCA_list = os.listdir(workingfoder)
    # iterate every small text file and run NCBI-GENOMIE-DOWNLOAD
    for file in GCA_list: 
        if file.startswith('missing_GCAs_'):

            NCBI_download= "ncbi-genome-download -F fasta -s genbank -A "+file+" --human-readable -o temp all"
            NCBI_args = shlex.split(NCBI_download)
            print("Start downloading:" + file)
            p = subprocess.call(NCBI_args)
            




if __name__ == "__main__":
    main(sys.argv)
