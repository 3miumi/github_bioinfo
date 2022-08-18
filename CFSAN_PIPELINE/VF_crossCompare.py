
from unittest import result
import sys, os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import time
import json
from collections import defaultdict
import shlex, subprocess
from subprocess import CalledProcessError
import pathlib
import csv  





def main(args):    
    opts = parse_cmdline_params(args[1:])
    os.chdir(opts.folder)
    location = opts.folder
    # find if the samples(w number) existed or not
    samples = opts.filename
    VFsampleList = []

    AllSample = {}

    for sample in samples:
        sampleFolder = os.path.join(location,sample)
        if not os.path.exists(sampleFolder):
            print(str(sample) + "not existed")
            exit()

        # find if the VF file exists or not
        cease = True
        for file in os.listdir(os.path.join(sampleFolder,"srst2")):
            if "VirFactors__fullgenes" in file:
                cease = False
        if cease == True:
            print("Virulence Factors file not found")
            exit()

        # get species
        os.chdir(sampleFolder)
        species = ""
        with open('results.json', 'r') as f:
            datafile = json.load(f)
            for i in datafile:
                value = datafile[i]
                if value.get("mashID"):
                    species = value.get("mashID").get("Species")
                    # VFsampleList.append(species)

        VF_dict = defaultdict(list)
        VF_dict["species"].append(species)
        count = 0
        for file in os.listdir(os.path.join(sampleFolder,"srst2")):
            if "VirFactors__fullgenes" in file:
                with open (os.path.join(sampleFolder,"srst2",file), 'r') as vf :
                    for line in vf:
                        count += 1
                        if count == 1:
                            continue
                        row = line.strip().split("\t")
                        if row[0] not in VF_dict["header"]:
                            VF_dict["header"].append(row[0])
                        if row[1] not in VF_dict["DB"]:
                            VF_dict["DB"].append(row[1])
                        if row[2] not in VF_dict["gene"]:
                            VF_dict["gene"].append(row[2])
                            VF_dict["annotation"].append(row[-1])
                        print("Line{}: {}".format(count, line.strip()))
       
        length_of_gene = len(VF_dict["gene"])
        print(length_of_gene)
        if length_of_gene > 36:
             filter(VF_dict, species)
        AllSample[sample] = VF_dict



    header, sampleList = crossCompare(AllSample)
    
    os.chdir(opts.folder)
    with open('VF_crossCompparison.csv', 'w',newline='') as f:
        writer = csv.writer(f)
        # write the header
        writer.writerow(header)

        # write the data
        writer.writerows(sampleList)




    

                  
def filter(sample_VF, species):
    dataset = ""
    if species.split()[0] == "Salmonella":
        dataset = "Sal_Major_VF.txt"
    elif species.split()[0] == "Listeria":
        dataset = "Listeria_Major_VF.txt"
    elif species.split()[0] == "Escherichia":
        dataset = "Ecoli_Major_VF.txt"


    datasetPath = os.path.join("C:\\Users\\ming\\Documents\\VirFactor",dataset)
    majorVF = set()
    with open(datasetPath, 'r') as f:
        for line in f:
            row = line.strip().split("\t")
            majorVF.add(row[0].lower())
    
    ori_gene = sample_VF['gene']
    ori_annotation = sample_VF['annotation']

    for i in range(len(ori_gene)-1, -1,-1):
        if ori_gene[i].lower() not in majorVF:
            ori_gene.pop(i)
            ori_annotation.pop(i)
    
    sample_VF['gene'] = ori_gene
    sample_VF['annotation'] = ori_annotation





def crossCompare(allSamples):
    header = ['MEI ID',  'Organism', "DB"]
    sampleList = []
    date = []
    vf_resist = []
    antigenCount = 0
    
    for sample in allSamples:
        
        value = allSamples[sample]
        innerSample = []     

        innerSample.append("".join(value.get("header")))
        innerSample.append("".join(value.get("species", "NA")) )
        innerSample.append("".join(value.get("DB")) )
        
        # if "serovar" in value.get("mashID").get("Species"):
        #     innerSample.append(value.get("mashID").get("Species").split("serovar")[0])
        #     innerSample.append(value.get("mashID").get("Species").split("serovar")[1])
        # else:
        #     innerSample.append(value.get("mashID").get("Species")) 
        #     innerSample.append("NA")
        # else:
        #     innerSample.extend(list(["NA","NA", "NA"]))

        
        if value.get('gene'):
            
            
            antigens = value.get("gene")
            for antigen in antigens:

                if antigen not in header: antigenCount += 1 
                if antigen not in header: header.append(antigen) 
        sampleList.append(list(innerSample))


    ab_resist = ["-"] * antigenCount
    for elem in sampleList:
        elem.extend(ab_resist)
    sampleCout = 0
    for i in allSamples: 
        value = allSamples[i]
        if value.get('gene'):
            for j in range(3,len(header)):
                if header[j] in value.get("gene"):
                    sampleList[sampleCout][j] = "+" 
        sampleCout +=1 

    return header, sampleList

  

    
def parse_cmdline_params(arg_list):
    """Parses commandline arguments.
    :param arg_list: Arguments to parse. Default is argv when called from the
    command-line.
    :type arg_list: list.
    """
    #Create instance of ArgumentParser
    options_parser = ArgumentParser(formatter_class=
                                    ArgumentDefaultsHelpFormatter)
    options_parser.add_argument('--filename', dest='filename', type=str, required=True, nargs='+',
                                help="W numbers that need to be compared, seperated by space")
    options_parser.add_argument('--folder', dest='folder', type=str, required=True,
                                help="folder name to find")
    opts = options_parser.parse_args(args=arg_list)
    return opts






    
if __name__ == "__main__":
    main(sys.argv)

# importing the csv module
# import csv
 
# # field names
# fields = ['Name', 'Branch', 'Year', 'CGPA']
 
# # data rows of csv file
# rows = [ ['Nikhil', 'COE', '2', '9.0'],
#          ['Sanchit', 'COE', '2', '9.1'],
#          ['Aditya', 'IT', '2', '9.3'],
#          ['Sagar', 'SE', '1', '9.5'],
#          ['Prateek', 'MCE', '3', '7.8'],
#          ['Sahil', 'EP', '2', '9.1']]
 
# # name of csv file
# filename = "university_records.csv"
 
# # writing to csv file
# with open(filename, 'w') as csvfile:
#     # creating a csv writer object
#     csvwriter = csv.writer(csvfile)
     
#     # writing the fields
#     csvwriter.writerow(fields)
     
#     # writing the data rows
#     csvwriter.writerows(rows)