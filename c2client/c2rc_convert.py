import sys
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=argparse.FileType("r"),
            help="Path to c2rc.sh file.")
    parser.add_argument("outfile", nargs="?", type=argparse.FileType("w"),
            default=sys.stdout, help="Path to c2rc.bat file. Prints to screen if not set.")
    args = parser.parse_args()
    return args


def convert(infile, outfile):
    for line in infile:
        if line.startswith("#"):
            continue

        s = line.replace("export", "SET")
        s = s.replace("${", "%")
        s = s.replace("}", "%")

        if '"$' in s:
            s = s.replace('"', '%"')
            s = s.replace('%"$', '"%')

        s = s.replace('"', "")
        outfile.write(s)


def main():
    args = parse_args()
    convert(args.infile, args.outfile)
