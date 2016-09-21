require([
    'jquery',
    'underscore',
    'knockout',
    'views/page-view',
    'views/resource/editor/form-list',
    'models/card',
    'resource-editor-data',
    'widgets',
    'bindings/sortable'
], function($, _, ko, PageView, FormList, CardModel, data, widgets) {
    var self = this;
    var formList = new FormList({
        forms: ko.observableArray(data.forms)
    })

    this.card = new CardModel({
        data: data.form.forms[0].cardgroups[0],
        datatypes: data.datatypes
    });

    if(this.card.isContainer()){
        this.selection = ko.observable(self.card.get('cards')()[0]);
    }else{
        this.selection = ko.observable(this.card);
    }
    this.currentTabIndex = ko.computed(function () {
        if (!self.card.isContainer()) {
            return 0;
        }
        var card = self.selection();
        if (card.node) {
            card = card.card;
        }
        var index = self.card.get('cards')().indexOf(card);
        return index;
    });

   

    /**
    * a PageView representing the resource listing and recent edits page
    */
    var pageView = new PageView({
        viewModel:{
            formList: formList,
            card: this.card,
            selection: this.selection,
            widgetLookup: widgets,
            currentTabIndex: this.currentTabIndex,
            currentTabCard: ko.computed(function () {
                if(self.card.get('cards')().length === 0){
                    return self.card;
                }else{
                    return self.card.get('cards')()[self.currentTabIndex()];
                }
            }, this)

        }
    });

});
