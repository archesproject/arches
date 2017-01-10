define([
    'underscore',
    'knockout',
    'views/search/base-filter',
    'search-data',
    'view-data',
    'bindings/datepicker',
    'bindings/chosen'
],
function(_, ko, BaseFilter, searchData, viewData) {
    return BaseFilter.extend({
        initialize: function(options) {
            this.fromDate = ko.observable(null);
            this.toDate = ko.observable(null);
            // this.dateRangeType = ko.observable('today');
            this.graphs = _.filter(viewData.graphs, function(graph) {
                    return graph.isresource && graph.isactive;
                }).map(function(graph){
                    return _.extend(graph, {
                        dateNodes: _.filter(searchData.date_nodes, function(node) {
                            return graph.graphid === node.graph_id;
                        })
                    })
                }).filter(function(graph) {
                    return graph.dateNodes.length > 0;
                })
            console.log(this.graphs);


            this.dateRangeType = ko.pureComputed({
                read: function() {
                    return 'today';
                },
                write: function(value) {
                    if (value !== 'custom'){

                    }
                    // set date range value based on selection
                },
                owner: this
            });
            this.dateRangeType.subscribe(function(value) {
                if (value !== 'custom'){
                    updatingDateRange = true;
                    // TODO: update from & to dates

                }
                updatingDateRange = false;
            });


            BaseFilter.prototype.initialize.call(this, options);
        },

        appendFilters: function(queryStringObject) {
            return false;
        },

        restoreState: function(filter) {
            return;
        },

        clear: function() {
            return;
        }
    });
});
