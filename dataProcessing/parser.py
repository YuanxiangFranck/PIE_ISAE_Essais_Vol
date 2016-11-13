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



def txt_parser(file_name):
    """
    Read file_name and parse the data

    :param file_name: string
        path to the file to parse

    :out: pd.DataFrame
        data in the text file
    """
    # Fist 5 lines are description of the flight
    # Line 6 represent the aquisition channel ????
    # Line 7 are the signals name
    # Line 8 contains the units of each line
    # Line 10 gives aquisition time TO_CHECK!!!!
    df = pd.read_csv(file_name, header=[7, 8], skiprows=[10], sep="	")

    # Sampling rate = 1, so to avoid computation get relative time using index
    rtime = df.index # df["Time"].iloc[:, 0] - df["Time"].iloc[0, 0]
    df["rTime"] = pd.DataFrame({"sec": rtime})

    # If -999999 is in the last row remove it
    if -999999.0 in df.iloc[-1, :].data:
        return df.iloc[:-1]
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
    data = txt_parser(args.txt_file)
