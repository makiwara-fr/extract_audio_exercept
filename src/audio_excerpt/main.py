# -*- coding: utf-8 -*-
# ###################################################################################
#
#             Your text
#
#    License:
#    Author:
#
#                    __   .__
#      _____ _____  |  | _|__|_  _  _______ ____________
#     /     \\__  \ |  |/ /  \ \/ \/ /\__  \\_  __ \__  \
#    |  Y Y  \/ __ \|    <|  |\     /  / __ \|  | \// __ \_
#    |__|_|  (____  /__|_ \__| \/\_/  (____  /__|  (____  /
#          \/     \/     \/                \/           \/
#
#    Program walks through a directory (and subs), watch for audio and 
#   extract an excerpt save the new file   
# 
# ######################################################################



import sys
import re
import os
from pathlib import Path
import argparse
import yaml
from yaml.loader import SafeLoader
import ffmpeg



def set_regexp(suffix_list):
    """ set the regex to look for audio files """
    regexp = ""
    for suf in suffix_list:
        if regexp == "":
            regexp += f"({suf}"
        else:
            regexp += f"|{suf}"
	#finalize the string if not empty
    if regexp != "":
        regexp += f")"
        return re.compile(regexp)
    else:
        return None


def scan_folder(wd, regexp):
    """ scan folder for files mathcing regexp"""
    files_list = []	
	
    # Scanning folder
    print(f"Scanning folder : {wd}")
    
    # scanning all the files  #for entry in os.scandir(wd):
    for entry in Path(wd).iterdir():
        if entry.is_file():
			# recognize if videos
            if regexp.search(entry.name):
				#print(entry.name)
                files_list.append(entry)
        elif entry.is_dir():
            files_list += scan_folder(entry.path, regexp)
        else:
			#need to work on recursive folders structure
            pass
	
    return files_list
	
def extract(file, output_dir, beg, end):
    """ extract except from given file and put results in output dir taking audio only for beg to end """
    infile = Path.cwd().joinpath(file)
    print(infile)
    outfile = Path.cwd().joinpath(output_dir, file.stem + '_extract.mp3')

    try:
        
        #command = f"ffmpeg -i \"{infile}\" -ss {beg} -to {end}  -af \"afade=t=out:st={end-5}:d=5\"  -y \"{outfile}\""
        # reencode if not MP3 file
        if infile.suffix != ".mp3":
            print("not mp3", infile.suffix)
            reencode = " -codec:a libmp3lame "
        else:
            reencode =""

        command = f"ffmpeg -i \"{infile}\" -ss {beg} -to {end}  -af \"afade=t=out:st={end-5}:d=5\" {reencode} -y \"{outfile}\""

        #command = f"ffmpeg -i \"{infile}\" -ss {beg} -to {end}  -af \"afade=t=out:st={end-5}:d=5\" -c copy -y \"{outfile}\""
        #print(command)
        status = os.system(command)
        return status
        #return 0
    except Exception as e:
        print(e)
        return 1

    
    return res



def main():
     # Welcome messages
    print("")
    print("")
    print("")
    print("".join((
    "                 __   .__                              \n",
    "   _____ _____  |  | _|__|_  _  _______ ____________   \n",
    "  /     \\\\__  \ |  |/ /  \ \/ \/ /\__  \\\\_  __ \\__  \\  \n",
    " |  Y Y  \/ __ \|    <|  |\     /  / __ \|  | \// __ \_\n",
    " |__|_|  (____  /__|_ \__| \/\_/  (____  /__|  (____  /\n",
    "      \/     \/     \/                \/           \/ \n")))
    print("")
    print("")
    print("")
    print("-------------")
    print("Audio excerpt")
    print("-------------")

    # Open the file and load the file
    
    with open("parameters.yaml") as f:
        params = yaml.load(f, Loader=SafeLoader)
        

    # check quality 
    if not params['input_dir']:
        params['input_dir'] = "."
    if not params['output_dir']:
        params['output_dir'] = "."

    #print(params)



    # read input files
    # ----------------

    print(f"Working directory is {Path.cwd()}")

    regex = set_regexp(params['input_file_extension']) #list of extension to look for in directory
    print(regex)
    files_list = scan_folder(params['input_dir'], regex) #scanning the input directory
    if len(files_list)>0:
        print(f"found {len(files_list)} files" )
        print()
    else:
        sys.exit(0)
        print("exiting")
        print("")       

    end = params['last_second']
    beg = params['first_second']
    output_dir = params['output_dir'] + "/"

    # --------------------------
    # launch ffmpeg on file list
    # --------------------------
    status = 0
    error_files = []

    # real processing of files
    # -------------------------

    for f in files_list:
        if extract(f, output_dir, beg, end) == 0:
            status += 1
        else:
            error_files.append(f)

    # --------------
    # report results
    # --------------

    # check if all files have been processed
    if len(files_list)>0:
        results = status/len(files_list)
    else:
        results = 1.
    print(f"Processing done at {results*100:.0f}%")
    print()
    
    if len(error_files)>0:
        print("Something went wrong with these files")
        for ef in error_files:
            print("-", ef.name)
    print("")

if __name__ == "__main__":
    main()