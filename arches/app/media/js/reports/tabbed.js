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
            var self = this;
            params.configKeys = ['nodes'];
            ReportViewModel.apply(this, [params]);

            // this.tabs = ko.observableArray([]);
            // self.config()["tabs"].forEach( function(tab) { self.tabs().push(tab); });

            self.tabs = koMapping.fromJS(self.config()['tabs'])

            this.activeTab = ko.observable(self.tabs()[0]);

            // this.activeStatus = ko.pureComputed( function(tab) {
            //     return tab["name"] == self.activeTab["name"] ? "active-report-tab": "report-tab";
            // }, this);
            this.topcards = self.report.cards().map(function(card){
                return {name: card.model.name(), nodegroupid: card.nodegroupid};
            });

            this.makeActiveTab = function(tab) { self.activeTab(tab); };

            this.isActiveTab = function(checkTab) {
                self.tabs().forEach(function(tab) { if(tab["name"] == checkTab["name"]) { return true; } });
                return false;
            };

            this.cardInActiveTab = function(cardNodegroupId) {
                if (self.activeTab()) {
                    self.activeTab()["nodegroup_ids"]().forEach( function(tabNodegroupId) {
                        if (cardNodegroupId == tabNodegroupId) { return true; }
                    });
                }
                return false;
            };

            this.tabs.subscribe(function(tabs){
                console.log(tabs.length)
            })

            this.jsontabs = ko.pureComputed(function(){
                console.log(self.tabs()[0].name())
                return koMapping.toJS(self.tabs);
            });

            this.jsontabs.subscribe(function(tabs){
                console.log('updating config')
                console.log(self.report.configJSON().tabs.length, self.config().tabs.length)
                self.report.configJSON({tabs: koMapping.toJS(tabs)});
            });

            this.activeCards = ko.computed( function() {
                var cardList = [];
                ko.unwrap(self.report.cards).forEach(function(card) {
                    if (self.activeTab()) {
                        self.activeTab()["nodegroup_ids"]().forEach( function(tabNodegroupId) {
                            if(card.nodegroupid == tabNodegroupId) { cardList.push(card); }
                        });
                    }
                });
                return cardList;

                //(expression below) -- filter(...cardInActiveTab(...)) wasn't working for some reason
                // return self.report.cards().filter(function(card) { return self.cardInActiveTab(card.nodegroupid); });
            });

            this.addTab = function(){
                this.tabs.push({icon:'', name:'', nodegroup_ids:[]});
            };

            this.removeTab = function(tab){
                this.tabs.remove(tab);
            };

        },
        template: { require: 'text!report-templates/tabbed' }
    });
});
