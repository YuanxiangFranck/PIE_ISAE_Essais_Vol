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
"""
    with open('./signals_to_monitor.txt') as f_signals_to_monitor:
        signals_to_monitor = f_signals_to_monitor.readlines()
        # Some names contains
        get_name = lambda x: x.split("@")[1] if "@" in x else x
        signals_to_monitor = [get_name(s).strip() for s in signals_to_monitor]
    # Fist 7 lines are description of the flight
    # Line 9 is the name of each column in french but it's not usable because
    # some have spaces like «FLIGHT DECK AMBIENT TEMPERATURE 1»
    # Line 10 contains the units of each line
    # Line 11 gives aquisition time TO_CHECK!!!!
    df = pd.read_csv(file_name, header=7, skiprows=[9, 10, 11], delim_whitespace=True)
    # Filter the columns to get only the signals we need
    not_in_table = []
    to_keep = []
    for sig in signals_to_monitor:
        if sig in df.columns:
            to_keep.append(sig)
        else:
            logging.warning(sig+' was not found in the data')
            not_in_table.append(sig)
    logging.warning(str(len(not_in_table))+" not found")
    return df[to_keep]

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
