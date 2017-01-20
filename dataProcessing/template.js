var rest = 1;
var values = [];
var keys = [];
for (var k of Object.keys(stats)) {
    rest -= stats[k];
    values.push(stats[k]);
    keys.push(k);
}
keys.push("no phases");
values.push(rest);
var data = [{
    values: values,
    labels: keys,
    type: 'pie'
}];

var layout = {
    height: 400,
    width: 500
};
Plotly.newPlot('phases_stats_pie', data, layout);

var data = [];
var index = phases["index"];
var order =  ["otg", "take_off", "landing", "climb", "descent", "hold", "cruise"];
for (var phase of order) {
    var fill = phase=="otg"?'tozeroy':'tonexty';
    data.push({
        y: phases[phase],
        x: index,
        name: phase,
        fill: fill,
        type: "scatter"
    });
}

Plotly.newPlot('plot_phases', data, {height: 400 });
