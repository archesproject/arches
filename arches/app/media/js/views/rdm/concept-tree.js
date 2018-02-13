define([
    'jquery',
    'backbone',
    'arches',
    'jqtree'
], function($, Backbone, arches) {
    return Backbone.View.extend({

        events: {
            'tree.click': 'treeClick',
            'tree.move': 'moveNode'
        },

        initialize: function(options) {
            var self = this;
            this.model = options.model;

            this.tree = this.$el.tree({
                dragAndDrop: true,
                dataUrl: options.url,
                data: [],
                autoOpen: false
            });

            this.render();
        },

        render: function() {
            if (this._doNotRender) {
                return;
            }
            var self = this,
                node = self.$el.tree('getNodeById', this.model.get('id'));
            if (node) {
                // collapse the node while it's loading
                if (!node.load_on_demand) {
                    self.$el.tree('toggle', node);
                }
                $(node.element).addClass('jqtree-loading');
            }

            self.$el.tree(
                'loadDataFromUrl',
                null,
                function() {
                    var node;
                    if (self.model.get('id') !== '') {
                        node = self.$el.tree('getNodeById', self.model.get('id'));
                        if (node) {
                            self.$el.tree('selectNode', node);
                            self.$el.tree('scrollToNode', node);
                        }
                    }
                }
            );
        },

        treeClick: function(event) {
            // The clicked node is 'event.node'
            var node = event.node;
            if (! node.load_on_demand){
                this.$el.tree('toggle', node);
            }
            if (this.model.get('id') !== node.id) {
                this.trigger('conceptSelected', node.id);
            } else {
                event.preventDefault();
            }
        },

        moveNode: function(event) {
            var self = this,
                move_info = event.move_info;
            if ((move_info.position !== 'inside' && move_info.previous_parent.id === move_info.target_node.parent.id) ||
                (move_info.position === 'inside' && move_info.previous_parent.id === move_info.target_node.id)) {
                // here we're just re-ordering nodes
            } else {
                event.preventDefault();
                $.ajax({
                    type: "POST",
                    url: arches.urls.concept_relation.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', move_info.moved_node.id),
                    data: JSON.stringify({
                        'target_parent_conceptid': move_info.position === 'inside' ? move_info.target_node.id : move_info.target_node.parent.id,
                        'current_parent_conceptid': move_info.previous_parent.id
                    }),
                    success: function() {
                        var data = JSON.parse(this.data);
                        event.move_info.do_move();
                        self.trigger('conceptMoved', data.conceptid);
                    }
                });
            }
        }
    });
});
