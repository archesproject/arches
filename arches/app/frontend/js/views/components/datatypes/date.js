define(['knockout'], function(ko) {
    var name = 'date-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            var self = this;
            this.search = params.search;
            if (!this.search) {
                this.dateFormat = params.config.dateFormat;
                this.dateFormatOptions = ko.observableArray([{
                    'id': 'YYYY-MM-DD HH:mm:ssZ',
                    'name': 'ISO 8601 Time (YYYY-MM-DD HH:mm:ssZ)'
                }, {
                    'id': 'YYYY-MM-DD',
                    'name': 'ISO 8601 (YYYY-MM-DD)'
                }, {
                    'id': 'YYYY-MM',
                    'name': 'ISO 8601 Month (YYYY-MM)'
                }, {
                    'id': 'YYYY',
                    'name': 'CE Year (YYYY)'
                }]);
        
                this.onDateFormatSelection = function(val, e) {
                    this.dateFormat(e.currentTarget.value);
                };
            }

            if (this.search) {
                var config = params.node.config || params.datatype.defaultconfig;
                var filter = params.filterValue();
                this.dateFormat = config.dateFormat;
                this.op = ko.observable(filter.op || '');
                this.searchValue = ko.observable(filter.val || '');
                this.filterValue = ko.computed(function() {
                    return {
                        op: self.op(),
                        val: self.searchValue()
                    }
                }).extend({ throttle: 750 });
                params.filterValue(this.filterValue());
                this.filterValue.subscribe(function(val) {
                    params.filterValue(val);
                });
            }
        },
        template: { require: 'text!datatype-config-templates/date' }
    });
    return name;
});
