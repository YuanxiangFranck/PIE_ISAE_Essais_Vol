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
