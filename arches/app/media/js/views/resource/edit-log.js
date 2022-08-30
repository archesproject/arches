require([
    'jquery',
    'underscore',
    'knockout',
    'moment',
    'views/base-manager',
    'views/resource/resource-edit-history-data',
    'bindings/chosen'
], function($, _, ko, moment, BaseManagerView, data) {
    var ResourceEditLogView = BaseManagerView.extend({
        initialize: function(options){
            var self = this;
            var cards = data.cards;
            var edits = data.edits;
            var editTypeLookup = {
                'create': {icon: 'fa fa-chevron-circle-right fa-lg', color: 'bg-mint'},
                'tile edit': {icon: 'fa fa-repeat fa-lg', color: 'bg-purple'},
                'tile create': {icon: 'fa fa-plus fa-lg', color: 'bg-dark'},
                'tile delete': {icon: 'fa fa-minus fa-lg', color: 'bg-danger'},
                'delete edit': {icon: 'fa fa-minus fa-lg', color: 'bg-danger'}
            };

            var handleChildCards = function(card) {
                if (card.cards.length > 0) {
                    _.each(card.cards, function(subCard) {
                        _.each(_.where(edits, { nodegroupid: subCard.nodegroup_id }), function(match) { match.card = subCard; match.cardContainerName = card.name; });
                        handleChildCards(subCard);
                    }, this);
                }
            };

            var assignCards = function(){
                _.each(cards, function(card) {
                    _.each(_.where(edits, {nodegroupid: card.nodegroup_id}), function(match){match.card = card; match.cardContainerName = null;});
                    handleChildCards(card);
                }, this);
            };
            assignCards();

            var createFullValue = function(value, edit) {
                var full_value = {};
                function rounder(key, value) {
                    if (typeof value === 'number') {
                        return Math.round(value * 10000000) / 10000000;
                    }
                    return value;
                }

                _.each(value, function(v, k){
                    if (_.isObject(v) && v['features']) {
                        v = _.map(v['features'], function(feature){return JSON.stringify(feature['geometry'], rounder, 4);});
                    }
                    full_value[k] = {new_value: v};
                    if (edit.card) {
                        _.each(edit.card.nodes, function(node){
                            if (k == node.nodeid) {
                                full_value[node.nodeid].node = node;
                            }
                        }, this);
                    }
                });
                return _.map(full_value, function(v,k){return v;});
            };

            _.each(edits, function(edit){
                var datetime = moment(edit.timestamp);
                edit.time = datetime.format("HH:mm");
                edit.day = datetime.format('DD MMMM, YYYY');
                edit.editor = edit.user_email != '' ? edit.user_email : edit.user_username;
                edit.edit_type_icon = editTypeLookup[edit.edittype];
                if (edit.nodegroupid) {
                    edit.full_new_value = createFullValue(edit.newvalue, edit);
                    edit.full_old_value = createFullValue(edit.oldvalue, edit);
                    edit.full_new_provisional_value = createFullValue(edit.newprovisionalvalue, edit);
                    edit.full_old_provisional_value = createFullValue(edit.oldprovisionalvalue, edit);
                }
            });

            this.viewModel.displayname = data.displayname;
            this.viewModel.description = data.description;
            this.viewModel.sortOrder = ko.observable('time_desc');
            this.viewModel.edits = ko.observableArray(edits);
            this.viewModel.edits.sort(function(left, right) { return left.timestamp == right.timestamp ? 0 : (left.timestamp > right.timestamp ? -1 : 1); });
            this.viewModel.currentDate = moment().format('MMMM D, YYYY');

            this.viewModel.sortOrder.subscribe(function(val) {
                var sortConditions = {
                    'time_desc': {'property':'timestamp', 'direction': 'gt'},
                    'time_asc': {'property':'timestamp', 'direction': 'lt'},
                    'editor_asc': {'property':'user_email', 'direction': 'lt'},
                    'type_desc': {'property':'edittype', 'direction': 'gt'}
                };
                var sortProperty = sortConditions[val].property;
                var sortDirection = sortConditions[val].direction;
                if (sortDirection == 'gt') {
                    self.viewModel.edits.sort(function(left, right) { return left[sortProperty] == right[sortProperty] ? 0 : (left[sortProperty] > right[sortProperty] ? -1 : 1); });
                } else {
                    self.viewModel.edits.sort(function(left, right) { return left[sortProperty] == right[sortProperty] ? 0 : (left[sortProperty] < right[sortProperty] ? -1 : 1); });
                }
            });

            BaseManagerView.prototype.initialize.call(this, options);
        }
    });
    return new ResourceEditLogView();
});
