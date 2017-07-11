require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'moment',
    'resource-edit-history-data',
    'views/base-manager',
    'bindings/chosen'
], function($, _, ko, arches, moment, data, BaseManagerView) {
    var ResourceEditLogView = BaseManagerView.extend({
        initialize: function(options){
            var self = this;
            var cards = data.cards;
            var edits = data.edits;
            var editTypeLookup = {
                'create': {icon: 'fa fa-chevron-circle-right fa-lg', color: 'bg-mint'},
                'tile edit': {icon: 'fa fa-repeat fa-lg', color: 'bg-purple'},
                'tile create': {icon: 'fa fa-plus fa-lg', color: 'bg-dark'},
                'tile delete': {icon: 'fa fa-minus fa-lg', color: 'bg-danger'}
            }

            _.each(edits, function(edit){
                var datetime = moment(edit.timestamp)
                edit.time = datetime.format("HH:mm");
                edit.day = datetime.format('DD MMMM, YYYY');
                edit.edit_type_icon = editTypeLookup[edit.edittype];
                console.log(edit.edit_type, edit.edit_type_icon)
                if (edit.attributenodeid) {
                    edit.card = _.findWhere(cards, {nodegroup_id: edit.attributenodeid})
                }
            })

            this.viewModel.edits = ko.observableArray(edits);
            this.viewModel.edits.sort(function (left, right) { return left.timestamp == right.timestamp ? 0 : (left.timestamp > right.timestamp ? -1 : 1) })
            this.viewModel.currentDate = moment().format('MMMM D, YYYY');
            this.viewModel.graph = data.graph;
            BaseManagerView.prototype.initialize.call(this, options);

        }
    });
    return new ResourceEditLogView();
});
