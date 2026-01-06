import ko from "knockout";
import _ from "underscore";
import fileListDatatypeTemplate from "templates/views/components/datatypes/file-list.htm";


const name = 'file-list-datatype-config';
const viewModel = function(params) {
    const self = this;
    this.config = params.config;
    this.search = params.search;

    if (this.search) {
        const filter = params.filterValue();
        this.op = ko.observable(filter.op || '~');
        this.node = params.node;
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
    } else {
        function stringify(val) {
            if (val == null) {
                return "";
            } else {
                return val.toString();
            }
        }
        this.maxFiles = ko.observable(stringify(params.config.maxFiles()));
        this.maxFiles.subscribe(function(val) {
            if (val === "" || val === null) {
                params.config.maxFiles(null);
                return;
            }

            const int = parseInt(val);
            if(!isNaN(int) && int > 0) { 
                params.config.maxFiles(int);
            } else {
                self.maxFiles(stringify(params.config.maxFiles()));
            }
        });
        params.config.maxFiles.subscribe(function(val) {
            const stringifiedVal = stringify(val);
            if (self.maxFiles() !== stringifiedVal) {
                self.maxFiles(stringifiedVal);
            }
        });

        this.imagesOnly = params.config.imagesOnly;
    }
};

ko.components.register(name, {
    viewModel: viewModel,
    template: fileListDatatypeTemplate,
});

export default name;
