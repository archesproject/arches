define([
    'jquery',
    'knockout',
    'd3',
    'nvd3'
], function ($, ko, d3, nv) {
    ko.bindingHandlers.nvd3Line = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext){

            var options = ko.unwrap(valueAccessor());
            var data = options.data;
            var $el = $(element);
            var width = $el.parent().width();
            var height = $el.parent().height();

            /*These lines are all chart setup.  Pick and choose which chart features you want to utilize. */
            nv.addGraph(function() {
              var chart = nv.models.lineChart()
                            .margin({left: 100})  //Adjust chart margins to give the x-axis some breathing room.
                            .useInteractiveGuideline(true)  //We want nice looking tooltips and a guideline!
                            // .transitionDuration(350)  //how fast do you want the lines to transition?
                            .showLegend(true)       //Show the legend, allowing users to turn on/off line series.
                            .showYAxis(true)        //Show the y-axis
                            .showXAxis(true)        //Show the x-axis
              ;

              chart.xAxis     //Chart x-axis settings
                  .axisLabel('x-axis')
                  .tickFormat(d3.format('.02f'));

              chart.yAxis     //Chart y-axis settings
                  .axisLabel('y-axis')
                  .tickFormat(d3.format('.02f'));

              /* Done setting the chart up? Time to render it!*/
              var myData = function() {
                    data( [
                            {x:2320.00,y:3228.68},
                            {x:2325.00,y:3102.83},
                            {x:2330.00,y:3328.01},
                            {x:2335.00,y:3160.01},
                            {x:2340.00,y:3076.24},
                            {x:2345.00,y:3161.03},
                            {x:2350.00,y:3063.17},
                            {x:2355.00,y:3147.99},
                            {x:2360.00,y:3078.21},
                            {x:2365.00,y:2980.3},
                            {x:2370.00,y:3079.2},
                            {x:2375.00,y:3135.95},
                            {x:2380.00,y:3108.32},
                            {x:2385.00,y:3151.02},
                            {x:2390.00,y:3123.39},
                            {x:2395.00,y:3053.53}
                        ])

                              return [
                                {
                                  values: data(),
                                  key: 'Test Data',
                                  color: '#ff7f0e'
                                }
                              ];
                            };

            var svg = d3.select(element).append("svg:svg")
                .datum(myData)
                .transition()
                .duration(800)
                .call(chart);

            data.subscribe(function(val){
                svg = d3.select($(element).find('svg')[0])
                getData = function(){ return [
                  {
                    values: val,
                    key: 'Test Data',
                    color: '#ff7f0e'
                  }
               ]};
                svg.datum(getData).transition().duration(800).call(chart);
               //  nv.utils.windowResize(chart.update);
            }, this);



              //Update the chart when window resizes.
              nv.utils.windowResize(function() { chart.update() });
              return chart;
            });


        }
    };

    return ko.bindingHandlers.nvd3;
});
