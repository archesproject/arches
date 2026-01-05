import ko from "knockout";
import _ from "underscore";
import fileListDatatypeTemplate from "templates/views/components/datatypes/file-list.htm";


var name = 'file-list-datatype-config';
const viewModel = function(params) {
    const self = this;
    this.config = params.config;
    this.search = params.search;

    if (this.search) {
        var filter = params.filterValue();
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
        this.maxFiles = ko.observable(
            params.config.maxFiles() == null ? "" : 
            params.config.maxFiles().toString()
        );
        this.maxFiles.subscribe(function(val) {
            if (val === "" || val === null) {
                params.config.maxFiles(null);
                return;
            }

            var int = parseInt(val);
            if(!isNaN(int) && int > 0) { 
                params.config.maxFiles(int);
            } else {
                self.maxFiles(
                    params.config.maxFiles() == null ? "" :
                    params.config.maxFiles().toString()
                );
            }
        });
        params.config.maxFiles.subscribe(function(val) {
            var stringified_val = (val === null ? "" : val.toString());
            if (self.maxFiles() !== stringified_val) {
                self.maxFiles(stringified_val);
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
