"""
Function to return a quick summary of the data

* % phase ????
* % non couvert
* plot vol phases
* nom

"""

from dataProcessing.parser import txt_parser
from dataProcessing.segmenter import segment, get_weights
from dataProcessing.plotter import Plotter

def compute_phases_index(phases, time):
    out_phases = {}
        for name, segments in phases.items():
            idx = np.zeros(time.size).astype(bool)
            for start, end in segments:
                idx = idx | ( (start < time) & (time < end ) )
            out_phases[name] = time.index[idx]
    return out_phases


def summary(path, out_path="results.html", data=None):
    "compute summary"
    # Get file header
    template_data = {}
    with open(path) as f:
        template_data["header"] = "".join([f.readline()+"</br>" for _ in range(6)])
    template_data["name"] = path.split("/")[-1]
    if data is None:
        data = txt_parser(path)
    phases = segment(data)
    template_data["phases"] = phases

    template_data["stats"] = get_weights(phases, data)
    with open("dataProcessing/template.css") as fc:
        template_data["css"] = fc.read()
    with open("dataProcessing/template.js") as fjs:
        template_data["js_code"] = fjs.read()
    with open('dataProcessing/template.html') as ft:
        template = ft.read()
    with open(out_path, "w") as f:
        f.write(template.format(**template_data))
