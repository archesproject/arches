define([
    'underscore',
    'knockout',
    'knockout-mapping',
    'jquery',
    'viewmodels/report',
    'arches',
    'knockstrap',
    'bindings/chosen',
    'views/components/widgets/map'
], function(_, ko, koMapping, $, ReportViewModel, arches) {
    return ko.components.register('tabbed-report', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['nodes'];
            ReportViewModel.apply(this, [params]);

            this.tabs = ko.observableArray([]);
            self.config()["tabs"].forEach( function(tab) { self.tabs().push(tab); });

            this.activeTab = ko.observable(self.tabs()[0]);

            // this.activeStatus = ko.pureComputed( function(tab) {
            //     return tab["name"] == self.activeTab["name"] ? "active-report-tab": "report-tab";
            // }, this);

            this.makeActiveTab = function(tab) { self.activeTab(tab); };

            this.isActiveTab = function(checkTab) {
                self.tabs().forEach(function(tab) { if(tab["name"] == checkTab["name"]) { return true; } });
                return false;
            };

            this.cardInActiveTab = function(cardNodegroupId) {
                self.activeTab()["nodegroup_ids"].forEach( function(tabNodegroupId) {
                    if(cardNodegroupId == tabNodegroupId) { return true; }
                });
                return false;
            };

            this.activeCards = ko.computed( function() {
                var cardList = [];
                self.report.cards().forEach(function(card) {
                    self.activeTab()["nodegroup_ids"].forEach( function(tabNodegroupId) {
                        if(card.nodegroupid == tabNodegroupId) { cardList.push(card); }
                    });
                });
                return cardList;

                //(expression below) -- filter(...cardInActiveTab(...)) wasn't working for some reason
                // return self.report.cards().filter(function(card) { return self.cardInActiveTab(card.nodegroupid); });
            });
        },
        template: { require: 'text!report-templates/tabbed' }
    });
});
