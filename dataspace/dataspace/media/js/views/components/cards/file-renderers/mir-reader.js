define(['jquery',
    'knockout',
    'viewmodels/afs-instrument',
    'bindings/plotly',
    'bindings/select2-query',
], function($, ko, AfsInstrumentViewModel) {
    return ko.components.register('mir-reader', {
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
                this.chartTitle("MIR Spectrum");
                this.xAxisLabel("Wavenumber/cm-1");
                this.yAxisLabel("log 1/R");
            };
        },
        template: { require: 'text!templates/views/components/cards/file-renderers/afs-reader.htm' }
    });
});
   
