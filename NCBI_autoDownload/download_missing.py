import os
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from glob import glob
import ntpath
import ftplib
from ftplib import FTP
from os import environ
#from sortedcontainers import SortedList


def main(args): 
    ftp = ftplib.FTP('ftp.ncbi.nlm.nih.gov')  
    ftp.login()
    print("connected to remote server : ftp.ncbi.nlm.nih.gov")
    print()
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
    
    
    # Parse command line parameters.
    opts = parse_cmdline_params(args[1:])


    """
    Functions for First Part:
    """
    def get_matadata_ftp(folder=""):
        contents = ftp.nlst(folder)
        folders = []
        for item in contents:
            if item[-1].isdigit():
                folders.append(item)

        # item : PDG00000001.XXXX, last for digit indicated the latest information
        folders.sort(key=lambda x: int(x.split(".")[1]))   

        return folders[len(folders)-1]


    # download tsv file through ftp
    def downloadFiles(path):
        try:
            # change into "path directory"
            ftp.cwd(path)
            # get local path    
            output_folder = os.getcwd()
            print ("Download to current directory: " + output_folder)
        except ftplib.error_perm:
            # invalid entry (ensure input form: "/dir/folder/something/")
            print ("error: could not change to "+path)
            sys.exit("ending session")


        #list children:
        filelist=ftp.nlst()

        for file in filelist:
            try:
                #this will check if file is folder:
                ftp.cwd(path+file+"/")
                #if so, explore it:
                downloadFiles(path+file+"/")
            except ftplib.error_perm:
                #not a folder with accessible content
                #download & return
                if file.endswith(".tsv"):
                    #possibly need a permission exception catch:
                    final_path_file = file
                    ftp.retrbinary("RETR "+file, open(os.path.join(output_folder,file).replace("\\","/"),"wb").write)
                    print (file + " downloaded")
        return final_path_file






    """
    First part : find the metadata.tsv through NCBI ftp
    1. find the latest path of metadata.tsv
    2. download tsv to current folder
    """

    # find the path: /pathogen/Results/species_name/PDG00000001.XXXX  /Metadata/
    Ftp_source_files_path = '/pathogen/Results/'+ opts.species
    Meta_folder = 'Metadata'

    # 1. find the latest path of metadata.tsv
    latest_path = get_matadata_ftp(Ftp_source_files_path)
    filepath = os.path.join(latest_path,Meta_folder).replace("\\","/")
    print("Find the latest folder in NCBI site:"+ filepath)

    # 2. download tsv to current folder
    final_path_file = downloadFiles(filepath)



    """ Second Part: In current folder, get the tsv file and start running missing_GCA/SRR """
    # Get list of SRR numbers from the metadata file.
    SRR_list = []
    # Decided not to use SortedList since we want them in chronological order.
    #SRR_list = SortedList()
    SRR_to_GCA = {}
    #open tsv file
    with open(final_path_file) as metaf:
        is_header = True
        SRR_index = -1
        GCA_index = -1
        for line in metaf:
            fields = line.split('\t')
            if is_header:
                is_header = False
                for i, field in enumerate(fields):
                    if field == 'Run':
                        SRR_index = i
                    elif field == 'asm_acc':
                        GCA_index = i
                assert(SRR_index >= 0)
            else:
                SRR_number = fields[SRR_index]
                GCA_number = fields[GCA_index]
                if len(SRR_number) > 0 and len(GCA_number) > 0 and SRR_number != 'NULL' and GCA_number != 'NULL':
                    #SRR_list.add(SRR_number)
                    SRR_list.append(SRR_number)
                    SRR_to_GCA[SRR_number] = GCA_number
    print('Number of SRR numbers in metadata file: ' + str(len(SRR_list)))

    # Remember old list of filenames to check for duplicates.
    previous_SRRs = set()
    # Subtract out the SRR assemblies already downloaded from the folders.
    print(opts.folders)
    #folders now is a list containing the path of target folder
    folders = opts.folders.split(',')
    for folder in folders:
        print(folder)
    for folder in folders:
        print('Subtracting out folder {}'.format(folder))
        # Get all assembled fasta files.
        filenames = [y for x in os.walk(folder) for y in glob(os.path.join(x[0], '*.fasta'))]
        filenames.extend( [y for x in os.walk(folder) for y in glob(os.path.join(x[0], '*.fna'))] )
        filenames.extend( [y for x in os.walk(folder) for y in glob(os.path.join(x[0], '*.fa'))] )
        # Also, this may be a mash folder so get all the mash filenames as well.
        filenames.extend( [y for x in os.walk(folder) for y in glob(os.path.join(x[0], '*.msh'))] )
        for filename in filenames:
            if os.path.isfile(filename):
                base_filename = os.path.splitext(ntpath.basename(filename))[0]
                # SRRxxxxxxx.fna, thus changed the split('_') to ('.')
                base_filename = base_filename.split('.')[0]
                if len(base_filename) > 0:
                    # If this filename was already seen, tell the user it's a duplicate.
                    if base_filename in previous_SRRs:
                        print('Dup: ' + base_filename)
                    # If it's not a duplicate...
                    else:
                        # Add this to the already-seen set.
                        previous_SRRs.add(base_filename)
                        # Remove this SRR from the metadata list, to get a list of just new ones that need to be downloaded.
                        try:
                            SRR_list.remove(base_filename)
                        except:
                            pass
        print('Number of SRR numbers after subtracting ({0}): {1}'.format(folder, len(SRR_list)))
    # Output the SRRs that still need to be downloaded.
    print('Outputting missing SRRs...')
    with open('missing_SRRs.txt', 'w') as outf:
        # Writing out in REVERSE chronological order to download the latest assemblies first!
        for SRR in SRR_list[::-1]:
            outf.write(SRR + '\n')
    print('Outputting missing GCAs...')
    with open('missing_GCAs.txt', 'w') as outf:
        for SRR in SRR_list[::-1]:
            outf.write(SRR_to_GCA[SRR] + '\n')
    # Aspera download NO LONGER WORKS with SRA files, sadly. Now using the missing_SRRs.txt list with prefetch --option-file missing_SRRs.txt
    #with open('download_missing_SRRs.sh', 'w') as outf:
    #    for SRR in SRR_list[::-1]:
    #        outf.write('ascp -T -l640M -i ~/asperaweb_id_dsa.openssh anonftp@ftp.ncbi.nlm.nih.gov:/sra/sra-instant/reads/ByRun/sra/{}/{}/{}/{}.sra .\n'.format(SRR[:3], SRR[:6], SRR, SRR))









if __name__ == "__main__":
    #debug_args = [sys.argv[0], '--metadata', 'C:\\ieh_input_data\\NCBI_Pathogen_metadata\\Listeria_PDG000000001.2231.metadata.tsv', '--folders', 'C:\\ieh_input_data\\NCBI_Pathogen_metadata\\test_assembly_folder']
    main(sys.argv)
    
