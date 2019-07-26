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

            this.refreshTab = function(tab){
                console.log('refershing lkdjsf')
                tab.name.subscribe(function(){
                    self.tabs.valueHasMutated();
                })
                tab.icon.subscribe(function(){
                    self.tabs.valueHasMutated();
                })
                tab.nodegroup_ids.subscribe(function(){
                    self.tabs.valueHasMutated();
                }, this);
            };

            this.tabs().forEach(function(tab){
                this.refreshTab(tab);
            }, this);

            this.addTab = function(){
                var newTab = koMapping.fromJS({
                    icon: '',
                    name: '',
                    nodegroup_ids: []
                });
                this.refreshTab(newTab);
                this.tabs.unshift(newTab);
            };

            this.removeTab = function(tab){
                this.tabs.remove(tab);
            };

        },
        template: { require: 'text!report-templates/tabbed' }
    });
});
