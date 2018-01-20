import os
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("input",help="path to input html file")
args = parser.parse_args()

def convert_html(file_path):
    cleanr = re.compile('<.*?>')
    
    output = os.path.basename(file_path)
    output = output.replace(".html","-tmp.txt")
    output = output.replace(".htm","-tmp.txt")
    
    with open(file_path,"rb") as opened:
        lines = opened.readlines()
        with open(output,"wb") as outfile:
            for line in lines:
                if "{% load i18n %}" in line:
                    continue
                if not "src=" in line:
                    line = re.sub(cleanr, '', line)
                line = line.replace('{% trans "',"")
                line = line.replace('" %}',"")
                line = line.replace('{% blocktrans %}',"")
                line = line.replace('{% endblocktrans %}',"")
                line = line.replace("&nbsp;","")
                if line.rstrip() == "":
                    continue
                outfile.write(line)
            
    
    print output
    
if __name__ == "__main__":
    
    
    convert_html(args.input)
    
    