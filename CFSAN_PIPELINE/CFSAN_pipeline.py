
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import sys,os
import shlex,shutil
import subprocess
from datetime import date
import download_SRRaccessions
import referenceChoser
from ete3 import Tree, TreeStyle, NodeStyle, AttrFace, faces, TextFace


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


    lines =  open("snp_distance_matrix.tsv", 'r').readlines()
    num = len(lines[0].split())
    lines[0] = str(num) + "\n"
    file = open("snp_distance_matrix.tsv", 'w')
    for line in lines:
        file.write(line)
    file.close()

    

    tree =  "fastme -i snp_distance_matrix.tsv -o " + sampleFolder + ".newick" 
    tree_args= shlex.split(tree)
    subprocess.call(tree_args)



def treeRead(tree):

    print(os.getcwd())
    # TODO:
    t = Tree(tree, quoted_node_names=True, format=1)
    print(t)
    style = TreeStyle()
    # style.mode = "r" # draw tree in circular mode
    style.show_leaf_name = True
    style.show_branch_length = False
    style.branch_vertical_margin = 5

    style.scale =  10
    
    # style.scale =  30
    style.margin_top = 15
    nst1 = NodeStyle()
    nst1["bgcolor"] = "yellow"
    nst2 = NodeStyle()
    nst2["fgcolor"] = "red"
    nst2["size"] = 10
    D_leaf_color = {tree:"red"}
    for n in t.traverse():
        n.img_style['size'] = 0
        if n.is_leaf():
            if tree in n.name  :
                # name_face = AttrFace("name", fsize=12, fgcolor="#009000")
                 # Adds the name face to the image at the preferred position
                # n.add_face_to_node(name_face, column=0)
                # faces.add_face_to_node(nameFace, n, column=0)
                color = D_leaf_color.get(n.name, None)
                if color:
                    name_face = TextFace(n.name, fgcolor=color, fsize=10)
                    n.add_face(name_face, column=0, position='branch-right')

            if "clinical" in n.name and tree not in n.name:
                n.set_style(nst2)
        
    # add title
    style.title.add_face(TextFace("Close isolates of " + tree, fsize=12), column=0)
    name_of_tree = tree + ".png"
    t.render(name_of_tree, tree_style=style)

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