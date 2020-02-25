define(['d3', 'marchingsquares'], function (d3, MarchingSquaresJS) {

    var intervals = [0, 4.5, 9, 13.5, 18];

    var data = [
        [18, 13, 10, 9, 10, 13, 18],
        [13, 8, 5, 4, 5, 8, 13],
        [10, 5, 2, 1, 2, 5, 10],
        [9, 4, 1, 12, 1, 4, 9],
        [10, 5, 2, 1, 2, 5, 10],
        [13, 8, 5, 4, 5, 8, 13],
        [18, 13, 10, 9, 10, 13, 18],
        [18, 13, 10, 9, 10, 13, 18]
    ];

    data = d3.transpose(data);
    var xs = d3.range(0, data[0].length);
    var ys = d3.range(0, data.length);

    var isoBands = [];
    for (var i = 1; i < intervals.length; i++) {
        var lowerBand = intervals[i - 1];
        var upperBand = intervals[i];
        var band = MarchingSquaresJS.isoBands(
                data,
                lowerBand,
                upperBand - lowerBand,
                {
                    successCallback: function (band) {
                        console.log('Band' + i + ':', band)
                    }
                }
        );
        isoBands.push({"coords": band, "level": i, "val": intervals[i]});
    }
    drawLines('#isobands', isoBands, intervals);


    // helper function
    function drawLines(divId, lines, intervals) {

        var marginBottomLabel = 0;

        var width = 300;
        var height = width * (ys.length / xs.length);

        var xScale = d3.scale.linear()
                .range([0, width])
                .domain([Math.min.apply(null, xs), Math.max.apply(null, xs)]);

        var yScale = d3.scale.linear()
                .range([0, height])
                .domain([Math.min.apply(null, ys), Math.max.apply(null, ys)]);

        var colours = d3.scale.linear().domain([intervals[0], intervals[intervals.length - 1]])
                .range([d3.rgb(0, 0, 0),
                    d3.rgb(200, 200, 200)]);

        var svg = d3.select(divId)
                .append("svg")
                .attr("width", width)
                .attr("height", height + marginBottomLabel);

        svg.selectAll("path")
                .data(lines)
                .enter().append("path")
                .style("fill", function (d) {
                    return colours(d.val);
                })
                .style("stroke", "black")
                .style('opacity', 1.0)
                .attr("d", function (d) {
                    var p = "";
                    d.coords.forEach(function (aa) {
                        p += (d3.svg.line()
                            .x(function (dat) {
                                return xScale(dat[0]);
                            })
                            .y(function (dat) {
                                return yScale(dat[1]);
                            })
                            .interpolate("linear")
                        )(aa) + "Z";
                    });
                    return p;
                })
                .on('mouseover', function () {
                    d3.select(this).style('fill', d3.rgb(204, 185, 116));
                })
                .on('mouseout', function () {
                    d3.select(this).style('fill', function (d1) {
                        return colours(d1.val);
                    })
                });

    }

});
