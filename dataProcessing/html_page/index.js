let Plotly = require('plotly.js/lib/core');

// Load in the trace types for pie, and choropleth
Plotly.register([
    require('plotly.js/lib/pie'),
    // require('plotly.js/lib/bar'),
    // require('plotly.js/lib/box')
]);
// Global variable from html:

// stats: data for phase % to plot pie chart
// phases: flight phases

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
    Plotly.newPlot('plot_phases', data, layout);
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
    Plotly.newPlot('phases_stats_pie', data, layout);

}

function plot_port_usage_per_phases(){
    let layout = {
        height: 400,
        width: 500
    };
    Plotly.newPlot('port_usage', ports_data, layout);
    layout.width = 1200;
    Plotly.newPlot('port_usage_side', ports_side_data, layout);
    layout.height = 600;
    Plotly.newPlot('port_usage_phases', ports_seg_data, layout);
}

plot_ratio_pie_chart();
plot_phases();
plot_port_usage_per_phases();
