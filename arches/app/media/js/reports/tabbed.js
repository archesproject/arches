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
            params.configKeys = ['tabs'];
            ReportViewModel.apply(this, [params]);
            var self = this;
            this.tabs(koMapping.fromJS(this.tabs())());
            this.activeTab = ko.observable(self.tabs()[0]);

            this.topcards = ko.unwrap(self.report.cards).map(function(card){
                return {name: card.model.name(), nodegroupid: card.nodegroupid};
            });

            this.cardInActiveTab = function(cardNodegroupId) {
                if (self.activeTab()) {
                    self.activeTab().nodegroup_ids().forEach( function(tabNodegroupId) {
                        if (cardNodegroupId === tabNodegroupId) { return true; }
                    });
                }
                return false;
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

            this.refreshTabs = function(){
                var data = self.tabs().slice(0);
                self.tabs([]);
                self.tabs(data);
            };

            this.tabs().forEach(function(tab){
                tab.nodegroup_ids.subscribe(function(){
                    this.refreshTabs();
                }, this);
            }, this);

            this.addTab = function(){
                var newTab = {
                    icon: ko.observable(),
                    name: ko.observable(),
                    nodegroup_ids: ko.observableArray()
                };
                newTab.nodegroup_ids.subscribe(
                    function(){this.refreshTabs();
                    }, this);
                this.tabs.unshift(newTab);
                this.refreshTabs();// this.tabs.valueHasMutated() not working here!?;
            };

            this.removeTab = function(tab){
                this.tabs.remove(tab);
                this.refreshTabs();
            };

        },
        template: { require: 'text!report-templates/tabbed' }
    });
});
