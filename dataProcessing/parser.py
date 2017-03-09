"""
Script to parse the data file
"""
import re
import pandas as pd
from dataProcessing.utils import logger


def arguments_parser():
    "Parse the arguments"
    import sys
    # Arguments
    parser = argparse.ArgumentParser(description=decription, formatter_class=RawTextHelpFormatter)
    parser.add_argument('txt_file', help='path to the text file (*.txt)')
    # Parse the arguments
    arguments = parser.parse_args(sys.argv[1:])
    logger.debug('args : '+str(arguments))
    return arguments



def txt_parser(file_name, name_line=8, nb_lines_to_skip=11, target_names=[]):
    """
    Read file_name and parse the data

    :param file_name: string
        path to the file to parse

    :out data: pd.DataFrame
        data in the text file
    """

    sep = "	"
    # Compute a dictionary with the units
    with open(file_name) as ff:
        for _ in range(name_line):
            ff.readline()
        names = ff.readline().strip().split(sep)

    df = pd.read_csv(file_name, skiprows=nb_lines_to_skip, names=names, sep=sep, engine="c")

    # Remove last line (often -9999999)
    df = df[:-1]
    # Compute relative time
    df["rTime"] = df["Time"] - df["Time"][0]

    # Add target regulation
    for c_name in target_names:
        # Add target like: 41psig
        m = re.search("\d*(?=psig)", c_name)
        if m:
            df[c_name] = int(m.group(0))
        # Check again if target is in data
        if c_name not in df.columns:
            logger.warning("target {}: not in Data".format(c_name))
    return df


if __name__ == "__main__":
    import argparse
    from argparse import RawTextHelpFormatter
    decription = '''
Script to parse the data file
'''
    # Parse arguments
    args = arguments_parser()
    # Parse the data
    logger.info("Read: "+ args.txt_file+"\n")
    data = txt_parser(args.txt_file)
