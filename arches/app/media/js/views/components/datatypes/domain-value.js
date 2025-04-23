import ko from 'knockout';
import uuid from 'uuid';
import _ from 'underscore';
import domainValueDatatypeTemplate from 'templates/views/components/datatypes/domain-value.htm';


const name = 'domain-value-datatype-config';
const viewModel = function(params) {
    var self = this;
    this.search = params.search;
        
    if (this.search) {
        this.options = params.node.config.options;
        this.options.unshift({id:"", selected:true, text:"Select an Option"});
        var filter = params.filterValue();
        this.node = params.node;
        this.op = ko.observable(filter.op || 'eq');
        this.searchValue = ko.observable(filter.val || '');
        this.filterValue = ko.computed(function() {
            return {
                op: self.op(),
                val: self.searchValue()
            };
        });
        params.filterValue(this.filterValue());
        this.filterValue.subscribe(function(val) {
            params.filterValue(val);
        });

    } else {
        this.options = params.config.options;
        params.config.options().map(option => { 
            option.text = ko.observable(ko.unwrap(option.text));
            option.text.subscribe(value => {
                if(value != option.text) {
                    self.options.valueHasMutated();
                }
            });
            return option;
        });
        var setupOption = function(option) {
            option.remove = function() {
                self.options.remove(option);
            };
        };
        this.options().forEach(setupOption);
        this.newOptionLabel = ko.observable('');
        this.addNewOption = function() {
            var option = {
                id: uuid.generate(),
                selected: false,
                text: ko.observable(self.newOptionLabel())
            };
            setupOption(option);
            self.options.push(option);
            self.newOptionLabel('');
        };
        if (ko.isObservable(this.options)) {
            this.options.subscribe(function(opts){
                _.each(opts, function(opt){
                    if (!opt.remove) {
                        setupOption(opt);
                    }
                });
            }, this);
        }
    }
};

ko.components.register(name, {
    viewModel: viewModel,
    template: domainValueDatatypeTemplate,
});

export default name;
