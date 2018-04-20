define([
    'underscore',
    'knockout',
    'views/base-manager',
    'resource-editor-data',
    'bindings/resizable-sidepanel'
], function(_, ko, BaseManagerView, data) {
    console.log(data);
    var cards = [];
    var tiles = ko.observableArray(data.tiles);
    _.each(data.cards, function (card) {
        cards.push(card);
    });
    var viewModel = {
        graphid: ko.observable(data.graphid)
    }

    return new BaseManagerView({
        viewModel: viewModel
    });
});
