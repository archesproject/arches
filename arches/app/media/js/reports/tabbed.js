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
], function(_, ko, koMapping, $, ReportViewModel) {
    return ko.components.register('tabbed-report', {
        viewModel: function(params) {
            params.configKeys = ['tabs', 'activeTabIndex'];
            ReportViewModel.apply(this, [params]);
            var self = this;
            this.activeTab = ko.observable(self.tabs()[ko.unwrap(this.activeTabIndex)]);
            this.report.configJSON.subscribe(function(){
                if (self.tabs.indexOf(self.activeTab()) === -1) {
                    self.activeTab(self.tabs()[ko.unwrap(this.activeTabIndex)]);
                }
            });
            this.topcards = ko.unwrap(self.report.cards).map(function(card){
                return {name: card.model.name(), nodegroupid: card.nodegroupid};
            });

            this.setActiveTab = function(tabIndex){
                self.activeTabIndex(tabIndex);
                self.activeTab(self.tabs()[ko.unwrap(self.activeTabIndex)]);
            };

            this.activeCards = ko.computed(function() {
                var cardList = [];
                ko.unwrap(self.report.cards).forEach(function(card) {
                    if (self.activeTab()) {
                        self.activeTab()["nodegroup_ids"]().forEach( function(tabNodegroupId) {
                            if(card.nodegroupid === tabNodegroupId) { cardList.push(card); }
                        });
                    }
                });
                return cardList;
            });

            this.addTab = function(){
                var newTab = koMapping.fromJS({
                    icon: '',
                    name: '',
                    nodegroup_ids: []
                });
                this.tabs.unshift(newTab);
                this.setActiveTab(0);
            };

            this.removeTab = function(tab){
                this.tabs.remove(tab);
                this.setActiveTab(0);
            };

        },
        template: { require: 'text!report-templates/tabbed' }
    });
});
