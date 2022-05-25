define(['jquery',
    'knockout',
    'viewmodels/afs-instrument',
    'bindings/plotly',
    'bindings/select2-query',
], function($, ko, AfsInstrumentViewModel) {
    return ko.components.register('raman-reader', {
        viewModel: function(params) {
            AfsInstrumentViewModel.apply(this, [params]);
            this.parse = function(data, series){
                var vals = data.split('\n');
                vals.forEach(function(val){
                    var rec = val.trim().split('\t');
                    if (Number(rec[1]) > 30 && rec[0] > 0.5) {
                        series.count.push(Number(rec[1]));
                        series.value.push(Number(rec[0]));
                    }
                });
                this.chartTitle("Raman Spectrum");
                this.xAxisLabel("Raman Shift (cm<sup>-1</sup>)");
                this.yAxisLabel("Intensity");
            };
        },
        template: { require: 'text!templates/views/components/cards/file-renderers/afs-reader.htm' }
    });
});
