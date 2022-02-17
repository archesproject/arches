define(['arches', 'knockout', 'uuid'], function (arches, ko, uuid) {
    ko.components.register('domain-value-datatype-config', {
        viewModel: function(params) {
            var self = this;
            this.search = params.search;
            if (this.search) {
                this.options = params.node.config.options;
                this.options.unshift({id:"", selected:true, text:"Select an Option"});
                var filter = params.filterValue();
                this.op = ko.observable(filter.op || '');
                this.searchValue = ko.observable(filter.val || '');
                this.filterValue = ko.computed(function () {
                    return {
                        op: self.op(),
                        val: self.searchValue()
                    }
                });
                params.filterValue(this.filterValue());
                this.filterValue.subscribe(function (val) {
                    params.filterValue(val);
                });

            } else {
                this.isEditable = true;

                if (params.graph) {
                    var cards = _.filter(params.graph.get('cards')(), function(card){return card.nodegroup_id === params.nodeGroupId()})
                    if (cards.length) {
                        this.isEditable = cards[0].is_editable
                    }
                } else if (params.widget) {
                    this.isEditable = params.widget.card.get('is_editable')
                }

                this.options = params.config.options;
                var setupOption = function(option) {
                    option.remove = function () {
                        self.options.remove(option);
                    };
                };
                this.options().forEach(setupOption);
                this.newOptionLabel = ko.observable('');
                this.addNewOption = function () {
                    var option = {
                        id: uuid.generate(),
                        selected: false,
                        text: ko.observable(self.newOptionLabel())
                    }
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
                        })
                    }, this)
                }
            }
        },
        template: { require: 'text!datatype-config-templates/domain-value' }
    });
    return name;
});
