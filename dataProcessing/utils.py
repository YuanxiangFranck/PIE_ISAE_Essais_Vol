from pathlib import Path
import logging

def check_dir(out_dir):
    "Check if directory exist before exporting"
    out_path = out_dir.split()
    tmp_out_dir = Path(".")
    for i, p in enumerate(out_path):
        tmp_out_dir = tmp_out_dir / p
        if not tmp_out_dir.exists():
            logging.warn("{} doesn't exist, try to create the directory".format("/".join(out_path[:i+1])))
            tmp_out_dir.mkdir()
