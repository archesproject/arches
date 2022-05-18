define([
    'jquery',
    'knockout',
    'Plotly'
], function($, ko, Plotly) {
    ko.bindingHandlers.plotly = {
        init: function(element, valueAccessor) {
            var config = ko.unwrap(valueAccessor());
            var chartData = {
                x: config.data().value,
                y: config.data().count,
                type: 'scatter',
                mode: 'lines',
                name: config.data().name,
                line: {
                    color: config.primarySeriesColor,
                    width: 3
                }
            };
            var layout = {
                title: {
                    text: config.title(),
                    font: {
                        family: 'Arial, monospace',
                        size: config.titleSize()
                    },
                    xref: 'paper',
                    x: 0.05,
                },
                xaxis: {
                    title: {
                        text: config.xAxisLabel(),
                        font: {
                            family: 'Arial, monospace',
                            size: config.xAxisLabelSize(),
                            color: '#7f7f7f'
                        }
                    },
                },
                yaxis: {
                    title: {
                        text: config.yAxisLabel(),
                        font: {
                            family: 'Arial, monospace',
                            size: config.yAxisLabelSize(),
                            color: '#7f7f7f'
                        }
                    }
                },
                legend: {
                    font: {
                        family: 'Arial, monospace',
                        color: '#7f7f7f'
                    }
                },
                width: $(element).width() - 2
            };

            var chartConfig = {
                responsive: false,
                modeBarButtonsToAdd: [{ 
                    name: 'expand height',
                    icon: {
                        'width': 1800,
                        'height': 1400,
                        'path': "M704 1216q0 -26 -19 -45t-45 -19h-128v-1024h128q26 0 45 -19t19 -45t-19 -45l-256 -256q-19 -19 -45 -19t-45 19l-256 256q-19 19 -19 45t19 45t45 19h128v1024h-128q-26 0 -45 19t-19 45t19 45l256 256q19 19 45 19t45 -19l256 -256q19 -19 19 -45z",
                    },
                    click: function() {
                        config.autosize = ko.unwrap(config.autosize) === undefined ? false : !ko.unwrap(config.autosize);
                        if (!ko.unwrap(config.autosize)) {
                            layout.height = ko.unwrap(config.height) || window.innerHeight - 250; //set custom height
                        } else {
                            layout.height = 450; //default
                        }
                        Plotly.relayout(element, layout);
                    }
                }]
            };

            this.chart = Plotly.newPlot(element, [chartData], layout, chartConfig);

            $(window).resize(function() {
                layout.width = $(element).width() - 2;
                Plotly.relayout(element, layout);
            });

            config.title.subscribe(function(val){
                layout.title.text = val;
                Plotly.relayout(element, layout);
            });

            config.titleSize.subscribe(function(val){
                layout.title.font.size = val;
                Plotly.relayout(element, layout);
            });

            config.xAxisLabel.subscribe(function(val){
                layout.xaxis.title.text = val;
                Plotly.relayout(element, layout);
            });

            config.xAxisLabelSize.subscribe(function(val){
                layout.xaxis.title.font.size = val;
                Plotly.relayout(element, layout);
            });

            config.yAxisLabel.subscribe(function(val){
                layout.yaxis.title.text = val;
                Plotly.relayout(element, layout);
            });

            config.yAxisLabelSize.subscribe(function(val){
                layout.yaxis.title.font.size = val;
                Plotly.relayout(element, layout);
            });

            config.seriesStyles.subscribe(function(val){
                var traceIndices;
                if(val.length >= 1) {
                    val.forEach(function(style) {
                        traceIndices = [];
                        element.data.forEach(function(trace, i){
                            if (trace.tileid === style.tileid) { traceIndices = [i]; }
                        });
                        if (traceIndices.length === 1) {
                            Plotly.restyle(element, {'marker.color': style["color"]}, traceIndices);
                        }
                    });
                }
            });

            config.seriesData.subscribe(function(val){
                val.forEach(function(series){
                    if (series.status === 'added') {
                        var style = config.seriesStyles().find(function(el){
                            return el["tileid"] === series.value.tileid;
                        });
                        Plotly.addTraces(element, {
                            x: series.value.data.value,
                            y: series.value.data.count,
                            opacity: 0.9,
                            marker: {
                                color: style.color,
                            },
                            name: series.value.name,
                            tileid: series.value.tileid,
                        }, element.data.length);
                    } else {
                        element.data.forEach(function(trace, i){
                            if (trace.name === series.value.name) {
                                Plotly.deleteTraces(element, i);
                            }
                        });
                    }
                });
            }, this, "arrayChange");

            ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            }, this); 
        },
    };
    return ko.bindingHandlers.plotly;
});
