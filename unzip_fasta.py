import os, gzip, shutil, sys
from datetime import date



def main():
    # if len(args) == 2:
    #     # if not sys.argv[1].endswith("/"):
    #         folder_name = sys.argv[1]
    
    dir_name = os.path.join(os.getcwd(),"temp/genbank/bacteria")
    # output_folder= folder_name
    # create a folder storing all unzipped fna files
    fna_dir = "fna_" + date.today().isoformat() 
    output_folder = os.path.join(os.getcwd(),fna_dir)
    if not os.path.isdir(output_folder):
        os.mkdir(output_folder)

    # gunzip the .gz file and remove the original files
    def gunzip(file_path,cwd,output_path):
        gz_name = os.path.abspath(os.path.join(cwd,file_path))# get full path of files
        basename =os.path.basename(gz_name)
        file_name = os.path.abspath(os.path.join(cwd,basename.rsplit('.',1)[0])) #get file name for file within
        with gzip.open(gz_name,"rb") as f_in, open(file_name,"wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(gz_name) # delete zipped file
        if os.path.isfile(file_name):
            shutil.copy2(file_name, output_path)



    # gunzip recursively 
    def recurse_and_gunzip(root):
        extension = ".gz"
        walker = os.walk(root)


        for root,dirs,files in walker:
            for f in files:
                if f.endswith(extension):
                    gunzip(f, root,output_folder)
            for dir in dirs:
                recurse_and_gunzip(dir)



    recurse_and_gunzip(dir_name)

if __name__== "__main__":
    main()