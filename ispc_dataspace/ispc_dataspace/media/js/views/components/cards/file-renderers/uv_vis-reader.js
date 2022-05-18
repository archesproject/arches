define(['jquery',
    'knockout',
    'viewmodels/afs-instrument',
    'bindings/plotly',
    'bindings/select2-query',
], function($, ko, AfsInstrumentViewModel) {
    return ko.components.register('uv_vis-reader', {
        viewModel: function(params) {
            const self = this;
            AfsInstrumentViewModel.apply(this, [params]);

            this.parse = function(data, series){
                const vals = data.split('\n');
                let metadata = {};
                vals.forEach(function(val) {
                    if (val.startsWith('##')) {
                        if (val.startsWith('##YFACTOR')) {
                            metadata.yfactor = Number(val.split('=')[1]);
                        }
                        if (val.startsWith('##XUNITS')) {
                            metadata.xunits = val.split('=')[1];
                        }
                        if (val.startsWith('##YUNITS')) {
                            const yunits = val.split('=')[1];
                            metadata.yunits = yunits ? `${yunits[0].toUpperCase()}${yunits.slice(1).toLowerCase()}` : '';
                        }
                    }
                    if (val.startsWith('Spectrum file is ')) {
                        const yunits = val.split(' ')[3];
                        metadata.yunits = yunits ? `${yunits[0].toUpperCase()}${yunits.slice(1).toLowerCase()}` : '';
                    }
                    let rec;
                    if (val.includes('\t')) {
                        rec = val.trim().split('\t');
                        if (Number(rec[0] >= 200 && rec[0] <= 2500)) {
                            series.value.push(Number(rec[0]));
                            series.count.push(Number(rec[1]));
                        }
                    } else {
                        rec = val.trim().split(/(?=[+-])/g);
                        if (Number(rec[0] >= 200 && rec[0] <= 2500)) {
                            series.value.push(Number(rec[0]));
                            rec.splice(0, 1);
                            const average = rec.reduce((a,b) => Number(a) + Number(b), 0) / rec.length;
                            series.count.push(average*metadata.yfactor);
                        }
                    }
                });
                self.chartTitle("UV-VIS Reflection");
                self.xAxisLabel("Wavelength (nm)");
                self.yAxisLabel( "R%");// metadata.yunits);
            };
        },
           template: { require: 'text!templates/views/components/cards/file-renderers/afs-reader.htm' }
    });
});

