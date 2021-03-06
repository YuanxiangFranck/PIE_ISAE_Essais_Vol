import "babel-polyfill";
import Plotly from 'plotly.js/lib/core';

// Load in the trace types for pie, and choropleth
Plotly.register([
    require('plotly.js/lib/pie'),
    // require('plotly.js/lib/bar'),
    // require('plotly.js/lib/box')
]);

// Handle window resiwe
window.addEventListener("resize", e=>{
    for (let node of document.querySelectorAll("div.plot-container.plotly")){
        Plotly.Plots.resize(node.parentNode);
    }
});
/*
Global variable from html:
* stats
* phases
* port_plot_data_1
* port_plot_data_2
* ports_side_data
* ports_seg_data

*/

function plot_phases(){
    let data = [];
    let index = phases["index"];
    let order =  ["otg", "take_off", "landing", "climb", "descent", "hold", "cruise"];
    for (let phase of order) {
        let fill = phase=="otg"?'tozeroy':'tonexty';
        data.push({
            y: phases[phase],
            x: index,
            name: phase,
            line: {shape: 'hv'},
            fill: 'tozeroy',
            type: "scatter"
        });
    }
    let layout = {height: 400, title: "Flight phases",
                  xaxis: {title: "Time (s)"},
                  yaxis: {title: "Phase", range:[0,8]}
                 };
    Plotly.newPlot('plot_phases', data, layout, {displaylogo: false});
}

function plot_ports(){
    let index = phases["index"];
    for (let data of port_plot_data_1) data.x = index;
    for (let data of port_plot_data_2) data.x = index;

    let layout = {height: 400, title: "Flight ports usage side 1",
                  xaxis: {title: "Time (s)"},
                  yaxis: {title: "Ports", range:[0,8]}
                 };
    Plotly.newPlot("plot_ports_side_1", port_plot_data_1, layout, {displaylogo: false});
    layout.title = "Flight ports usage side 2";
    Plotly.newPlot("plot_ports_side_2", port_plot_data_2, layout, {displaylogo: false});
}

function plot_ratio_pie_chart(){
    let rest = 1;
    let values = [];
    let keys = [];
    for (let k of Object.keys(stats)) {
        rest -= stats[k];
        values.push(stats[k]);
        keys.push(k);
    }
    keys.push("no phases");
    values.push(rest);
    let data = [{
        values: values,
        labels: keys,
        type: 'pie'
    }];

    let layout = {
        height: 400,
        width: 500
    };
    Plotly.newPlot('phases_stats_pie', data, layout, {displaylogo: false});

}

function plot_port_usage_per_side(){
    let layout = {height: 400, width: 500};
    Plotly.newPlot('port_usage', ports_data, layout);
    layout = {height: 400};
    layout.annotations = [{font: {size: 20}, showarrow: false, text:"Side: 1", x: 0.2, y:1},
                          {font: {size: 20}, showarrow: false, text:"Side: 2", x: 0.8, y:1}];
    Plotly.newPlot('port_usage_side', ports_side_data,
                   layout, {displaylogo: false});
}

function plot_port_usage_per_phases(){
    let annotations = [];
    for (let port_data of ports_seg_data){
        let x = port_data.domain.x[0]+.03;
        let y = port_data.domain.y[1]+.15;
        annotations.push({font: {size: 20}, showarrow: true,
                          text: port_data.name, arrowhead: 0,
                          x: x, y: y, ax:20, ay: 0});
    }
    let layout = {height: 700, annotations: annotations};
    Plotly.newPlot('port_usage_phases', ports_seg_data,
                   layout, {displaylogo: false});
}

plot_ratio_pie_chart();
plot_phases();
plot_ports();
plot_port_usage_per_side();
plot_port_usage_per_phases();
