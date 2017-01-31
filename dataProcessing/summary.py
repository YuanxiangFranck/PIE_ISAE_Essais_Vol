"""
Function to return a quick summary of the data

* % phase ????
* % non couvert
* plot vol phases
* nom

"""
import numpy as np
from dataProcessing.parser import txt_parser
from dataProcessing.segmenter import segment, get_weights

template_path = "dataProcessing/html_page/"

def compute_phases_index(phases, time):
    """
    Compute phases for the html page using the segmenter
    :param phases: dict
        dict with time range of each phases
    :param time : pd.Series
        time of the data
    :out : dict
        dict with the index of the different phases
    """
    order = ["otg", "take_off", "landing", "climb", "descent", "hold", "cruise"]
    out_phases = {}
    for nb, name in enumerate(order):
        segments = phases[name]
        idx = np.zeros(time.size).astype(bool)
        for start, end in segments:
            idx = idx | ( (start <= time) & (time <= end ) )
        idx = time.index[idx]
        # Create data
        plot = np.zeros(time.size)
        plot[idx] = nb+1
        out_phases[name] = plot.tolist()
    out_phases["index"] = time.tolist()
    return out_phases


def summary(path, out_path=None, out_dir="", data=None):
    """
    Compute summary

    * get html template
    * fill it with css code
    * fill it with bundled js code

    * Caution, need the js code to be built
    :param path: str
        path of the data file
    :param [out_path = None]: str
        path to export the html
    :param [data=None]: dataFrame
        data of the flight
    """
    # Get file header
    template_data = {}
    with open(path) as f:
        template_data["header"] = "".join([f.readline()+"</br>" for _ in range(6)])
    name = path.split("/")[-1][:-4] # Remove dir and ".txt" extention
    template_data["name"] = name
    if data is None:
        data = txt_parser(path)
    phases, ports = segment(data)
    plot_phases = compute_phases_index(phases, data.Time)
    template_data["phases"] = plot_phases

    template_data["stats"] = {k:int(v*100) for k, v in get_weights(phases, data).items()}
    css_txt = ""
    css_lib = ["bootstrap/dist/css/bootstrap.min.css"]
    css_lib = [template_path+ "node_modules/" + n for n in css_lib]
    for path in css_lib:
        with open(path) as fc:
            css_txt += fc.read()
    with open(template_path+"template.css") as fc:
        template_data["css"] = css_txt + fc.read()
    with open(template_path+"template.js") as fjs:
        template_data["js_code"] = fjs.read()
    with open(template_path+'template.html') as ft:
        template = ft.read()
    if out_path is None:
        out_path = out_dir + name+".html"
    with open(out_path, "w") as f:
        f.write(template.format(**template_data))
