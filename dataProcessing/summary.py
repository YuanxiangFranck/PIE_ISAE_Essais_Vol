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

def compute_phases_index(phases, time):
    order = ["otg", "take_off", "landing", "climb", "descent", "hold", "cruise"]
    out_phases = {}
    for nb, name in enumerate(order):
        segments = phases[name]
        idx = np.zeros(time.size).astype(bool)
        for start, end in segments:
            idx = idx | ( (start < time) & (time < end ) )
        idx = time.index[idx]
        # Create data
        plot = np.zeros(time.size)
        plot[idx] = nb+1
        out_phases[name] = plot.tolist()
    out_phases["index"] = time.tolist()
    return out_phases


def summary(path, out_path=None, out_dir="", data=None):
    "compute summary"
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

    template_data["stats"] = get_weights(phases, data)
    with open("dataProcessing/template.css") as fc:
        template_data["css"] = fc.read()
    with open("dataProcessing/template.js") as fjs:
        template_data["js_code"] = fjs.read()
    with open('dataProcessing/template.html') as ft:
        template = ft.read()
    if out_path is None:
        out_path = out_dir + name+".html"
    with open(out_path, "w") as f:
        f.write(template.format(**template_data))
