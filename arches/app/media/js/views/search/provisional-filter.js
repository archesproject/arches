define([
    'knockout',
    'views/search/base-filter'
], function(ko, BaseFilter) {
    return BaseFilter.extend({
        initialize: function(options) {
            BaseFilter.prototype.initialize.call(this, options);
            this.name = 'Provisional Filter';
            this.filter = ko.observableArray();
            this.provisionalOptions = [{'name': 'Authoritative'},{'name': 'Provisional'}]
        },

        restoreState: function(filter) {
            return;
        },


        selectProvisional: function(item) {
            this.filter().forEach(function(val){
                this.termFilter.removeTag(val.provisionaltype);
            }, this);

            if(!!item){
                var inverted = ko.observable(false)
                this.termFilter.addTag(item.name, this.name, inverted);
                this.filter([{provisionaltype: item.name, inverted: inverted}]);

            }else{
                this.clear();
            }

        },

        clear: function() {
            this.filter.removeAll();
        },

        appendFilters: function(filterParams) {
            if(this.filter().length > 0){
                filterParams.provisionalFilter = ko.toJSON(this.filter);
            }

            return this.filter().length > 0;
        }

    });
});
