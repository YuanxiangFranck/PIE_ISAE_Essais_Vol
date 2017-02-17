"""
Function to return a quick summary of the data

* % phase ????
* % non couvert
* plot vol phases
* nom

"""
import numpy as np
from dataProcessing.parser import txt_parser
from dataProcessing.segmenter import segment, get_weights, tuples_to_durations

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


def process_ports(ports, ports_full_flight):
    """
    Preprocessing the data for each plot of ports
    see plot_ports, plot_ports_sides, plot_ports_seg in segmenter
    """
    for each_segment in ports:
        ports[each_segment] = tuples_to_durations(ports[each_segment])
    ports_durations = tuples_to_durations(ports_full_flight)

    # Compute plot_ports data
    labels = [key for key in ports_durations]
    fracs = [ports_durations[key] for key in labels]
    ports_data = [{"labels": labels, "values":fracs,"type":"pie"}]

    # Compute plot_ports_sides
    labels_1 = [l for l in labels if l[-1]=='1'] + ['apu','no bleed'] # left pressure ports + apu
    labels_2 = [l for l in labels if l[-1]=='2'] + ['apu','no bleed'] # right pressure ports + apu
    fracs_1 = [ports_durations[key] for key in labels_1]
    fracs_2 = [ports_durations[key] for key in labels_2]
    ports_side_data = [{"labels": labels_1, "values":fracs_1,"type":"pie"},
                       {"labels": labels_2, "values":fracs_2,"type":"pie"}]

    # Compute plot_ports_seg
    ports_seg_data = {}
    for each_segment in ports:
        labels = ports[each_segment].keys()  # pressure ports names
        labels_1 = [label for label in labels if label[-1]=='1'] + ['apu','no bleed'] # left pressure ports + apu
        labels_2 = [label for label in labels if label[-1]=='2'] + ['apu','no bleed'] # right pressure ports + apu
        fracs_1 = [ports[each_segment][key] for key in labels_1]
        fracs_2 = [ports[each_segment][key] for key in labels_2]
        ports_seg_data[each_segment+"1"] = {"labels": labels_1, "values":fracs_1,"type":"pie"}
        ports_seg_data[each_segment+"1"] = {"labels": labels_2, "values":fracs_2,"type":"pie"}
    return ports_data, ports_side_data, ports_seg_data


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
    template_data = {}
    # Parse data and compute segmentation
    if data is None:
        data = txt_parser(path)
    phases, ports, ports_full_flight = segment(data)

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
