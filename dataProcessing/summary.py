"""
Function to return a quick summary of the data

* % phase ????
* % non couvert
* plot vol phases
* nom

"""
import numpy as np
from dataProcessing.parser import txt_parser
from dataProcessing.segmenter import segment
from dataProcessing.segmenter_utils import get_weights, tuples_to_durations

template_path = "dataProcessing/html_page/"

phases_order = ["otg", "take_off", "landing", "climb", "descent", "hold", "cruise"]
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
    out_phases = {}
    for nb, name in enumerate(phases_order):
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


def process_ports(ports, ports_full_flight):
    """
    Preprocessing the data for each plot of ports
    see plot_ports, plot_ports_sides, plot_ports_seg in segmenter
    """
    new_ports = {}
    for each_segment, ports_usage in ports.items():
        new_ports[each_segment] = tuples_to_durations(ports_usage)
    ports_durations = tuples_to_durations(ports_full_flight)

    # Compute plot_ports data
    labels = [key for key in ports_durations]
    fracs = [ports_durations[key] for key in labels]
    ports_data = [{"labels": labels, "values":fracs, "type":"pie"}]

    # Compute plot_ports_sides
    ports_side_data = []
    for side in [1, 2]:
        labels_tmp = [l for l in labels if l[-1] == str(side)] + ['apu', 'no bleed']
        fracs_tmp = [ports_durations[key] for key in labels_tmp]
        domain = {"y": [0, 0.8]}
        if side == 1:
            domain["x"] = [0, 0.48]
        else:
            domain["x"] = [0.52, 1]
        ports_side_data.append({"labels": labels_tmp, "values":fracs_tmp, "domain":domain,
                                "type":"pie", "name":"Side "+str(side)})

    # Compute plot_ports_seg
    ports_seg_data = []
    nb_ports = len(ports)
    for nb, each_segment in enumerate(phases_order):
        labels = new_ports[each_segment].keys()  # pressure ports names
        for side in [1, 2]:
            labels_1 = [l for l in labels if l[-1] == str(side)] + ['apu', 'no bleed']
            fracs_1 = [new_ports[each_segment][key] for key in labels_1]
            if sum(fracs_1) == 0:
                fracs_1.append(1)
                labels_1.append("no data")
            domain = {"x": [nb/nb_ports+.01, (nb+1)/nb_ports-.01]}
            if side == 1:
                domain["y"] = [.52, .8]
            else:
                domain["y"] = [0, 0.28]
            ports_seg_data.append({"labels": labels_1, "values":fracs_1,
                                   "domain": domain, "type":"pie",
                                   "name": each_segment+" "+str(side)})
    return ports_data, ports_side_data, ports_seg_data


def summary(path, out_path=None, out_dir="", data=None, phases_data=None):
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
    template_data = {}
    # Parse data and compute segmentation
    if data is None:
        data = txt_parser(path)
    if phases_data is None:
        phases, ports, ports_full_flight = segment(data)
    else:
        phases, ports, ports_full_flight = phases_data
    # Compute and add data for ports plot
    ports_data, ports_side_data, ports_seg_data = process_ports(ports, ports_full_flight)
    template_data["ports_data"] = ports_data
    template_data["ports_side_data"] = ports_side_data
    template_data["ports_seg_data"] = ports_seg_data

    # Compute and add data for phases
    plot_phases = compute_phases_index(phases, data.Time)
    template_data["phases"] = plot_phases
    template_data["stats"] = {k:int(v*100) for k, v in get_weights(phases, data).items()}

    # Add css to template
    css_txt = ""
    css_lib = ["bootstrap/dist/css/bootstrap.min.css"]
    css_lib = [template_path+ "node_modules/" + n for n in css_lib]
    for css_path in css_lib:
        with open(css_path) as fc:
            css_txt += fc.read()

    # Get file header
    with open(path) as f:
        template_data["header"] = "".join([f.readline()+"</br>" for _ in range(6)])
    name = path.split("/")[-1][:-4] # Remove dir and ".txt" extention
    template_data["name"] = name

    # Fill template
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
