import os       # for getting files from directory
import sys      # for accessing command line arguments
import glob


def main():
    # path = os.getcwd()
    # os.chdir(path)
    print (os.getcwd())
    with open('missing_GCAs.txt') as f:
        in_list  = [line.strip() for line in f]

    with open('missing_SRRs.txt') as f:
        out_list  = [line.strip() for line in f] 

    # under current folder
    folder_name = os.getcwd()

    # check if the current GCA is in the missing_GCA.txt
    def check(str):
        with open('missing_GCAs.txt') as f:
            datafile = f.readlines()
        found = False  # This isn't really necessary
        for line in datafile:
            if str in line:
                # found = True # Not necessary
                return True
        return False  # Because you finished the search without finding

    files_list = os.listdir(folder_name)
    print("debug")
    for dir in files_list: 
        # a folder named fna_xx-xx-xxxx(date) was created in current folder, and all fna were stored there  
        if dir.startswith('fna'):
            dir = os.path.join(folder_name,dir)
            for f in os.listdir(dir): # iterate over all files in files_list
                if f.endswith(".fna"): # check if FNA file (optional)
                    # split name GCA_019488765.1_PDT001103426.1_genomic 
                    tempF = f.split('_')[0] +"_"+ f.split('_')[1]
                    
                    if check(tempF):
                        print (tempF + ' becomes ' + out_list[in_list.index(tempF)]) # DEBUG
                        oriPath = os.path.join(dir,f)
                        finalPath = os.path.join(dir,out_list[in_list.index(tempF)]) + ".fna"
                        os.rename(oriPath,finalPath )
                    else:
                        print("GCA not found")


if __name__ == "__main__":
    print("Starting changing name...")
    main()
     
     