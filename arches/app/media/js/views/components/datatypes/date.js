import ko from 'knockout';
import dateDatatypeTemplate from 'templates/views/components/datatypes/date.htm';


var name = 'date-datatype-config';
const viewModel = function(params) {
    var self = this;
        
    this.search = params.search;
    if (!this.search) {
        this.dateFormat = params.config.dateFormat;
        this.dateFormatOptions = ko.observableArray([{
            'id': 'YYYY-MM-DD HH:mm:ssZ',
            'text': 'ISO 8601 Time (YYYY-MM-DD HH:mm:ssZ)'
        }, {
            'id': 'YYYY-MM-DD',
            'text': 'ISO 8601 (YYYY-MM-DD)'
        }, {
            'id': 'YYYY-MM',
            'text': 'ISO 8601 Month (YYYY-MM)'
        }, {
            'id': 'YYYY',
            'text': 'CE Year (YYYY)'
        }]);

        this.onDateFormatSelection = function(val, e) {
            this.dateFormat(e.currentTarget.value);
        };
    }

    if (this.search) {
        var config = params.node.config || params.datatype.defaultconfig;
        var filter = params.filterValue();
        this.dateFormat = config.dateFormat;
        this.node = params.node;
        this.op = ko.observable(filter.op || 'eq');
        this.searchValue = ko.observable(filter.val || '');
        this.filterValue = ko.computed(function() {
            return {
                op: self.op(),
                val: self.searchValue()
            };
        }).extend({ throttle: 750 });
        params.filterValue(this.filterValue());
        this.filterValue.subscribe(function(val) {
            params.filterValue(val);
        });
    }
};

ko.components.register(name, {
    viewModel: viewModel,
    template: dateDatatypeTemplate,
});

export default name;
