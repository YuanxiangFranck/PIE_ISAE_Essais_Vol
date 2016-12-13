"""
Script to parse the data file
"""
import logging
import pandas as pd


def arguments_parser():
    "Parse the arguments"
    import sys
    # Arguments
    parser = argparse.ArgumentParser(description=decription, formatter_class=RawTextHelpFormatter)
    parser.add_argument('txt_file', help='path to the text file (*.txt)')
    # Options
    parser.add_argument('-v', '--verbose', default=False, action="count",
                        help='Be more verbose\nNo option : warning level\n-v : info level\n -vv debug level')
    # Parse the arguments
    arguments = parser.parse_args(sys.argv[1:])
    logging.debug('args : '+str(arguments))
    # Basic arguments handling: Verbose / out path
    level = logging.INFO
    if arguments.verbose == 1:
        level = logging.INFO
    elif arguments.verbose >= 2:
        level = logging.DEBUG
    logging.basicConfig(format='%(levelname)s: %(message)s', level=level)
    return arguments



def txt_parser(file_name, get_units=False):
    """
    Read file_name and parse the data

    :param file_name: string
        path to the file to parse
    :param get_units=False: bool
        if true, it returns an additional dictionary with the units of each
        column

    :out data: pd.DataFrame
        data in the text file
    :out [units]: dict
        units of each column
    """

    sep = "	"
    # Compute a dictionary with the units
    with open(file_name) as ff:
        for _ in range(8):
            ff.readline()
        names = ff.readline().split(sep)
        units = ff.readline().split(sep)

    # Fist 5 lines are description of the flight
    # Line 7 represent the aquisition channel ????
    # Line 8 are the signals name
    # Line 9 contains the units of each line
    # Line 10 gives aquisition time TO_CHECK!!!!
    df = pd.read_csv(file_name, skiprows=11, names=names, sep=sep, engine="c")

    df = df[:-1]
    # Compute relative time
    df["rTime"] = df["Time"] - df["Time"][0]

    if get_units:
        unit_dict = {name: units[pos] for pos, name in enumerate(names) }
        return df, unit_dict
    # Remove last line
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
    logging.info("Read: "+ args.txt_file+"\n")
    data, units = txt_parser(args.txt_file, get_units=True)
