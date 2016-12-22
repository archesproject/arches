define([
    'jquery',
    'backbone',
    'arches',
    'knockout',
    'widgets/map',
    'views/search/base-filter'
    ],
    function($, Backbone, arches, ko, map, BaseFilter) {
        return BaseFilter.extend({
            initialize: function(options) {
                var self = this;
                BaseFilter.prototype.initialize.call(this, options);
                this.filter.terms = ko.observableArray();
                this.render();
            }
        });
    });
