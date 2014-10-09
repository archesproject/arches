define([
    'jquery',
    'backbone',
    'arches',
    'plugins/jqtree/tree.jquery.min'
], function($, Backbone, arches) {
    return Backbone.View.extend({

        events: {
            'tree.click': 'treeClick',
            'tree.move': 'moveNode'
        },

        initialize: function(options) {
            var self = this;

            $(this.el).tree({
                dragAndDrop: true,
                dataUrl: arches.urls.concept_tree,
                data: [],
                autoOpen: true
            });

            this.model.on('change', function () {
                self.render();
            });

            this.render();
        },

        render: function() {
            if (this._doNotRender) {
                return;
            }
            var self = this,
                tree = $(this.el),
                node = tree.tree('getNodeById', this.model.get('id'));
            if (node) {
                // collapse the node while it's loading
                if (!node.load_on_demand) {
                    tree.tree('toggle', node);
                }
                $(node.element).addClass('jqtree-loading');
            }

            tree.tree(
                'loadDataFromUrl',
                arches.urls.concept_tree + "?node=" + this.model.get('id'),
                null,
                function() {
                    var node;
                    if (self.model.get('id') === '') {
                        // get the top level concept from the tree
                        self._doNotRender = true;
                        self.model.set({ 'id': tree.tree('getTree').children[0].id });
                        self._doNotRender = undefined;
                    }

                    node = tree.tree('getNodeById', self.model.get('id'));
                    tree.tree('selectNode', node);
                    tree.tree('scrollToNode', node);
                }
            );
        },

        treeClick: function(event) {
            // The clicked node is 'event.node'
            var node = event.node;
            if (this.model.get('id') !== node.id) {
                this.model.set(node);
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
                if (confirm('Are you sure you want to move this concept to a new parent?')) {
                    $.ajax({
                        type: "POST",
                        url: arches.urls.concept_relation,
                        data: JSON.stringify({
                            'conceptid': move_info.moved_node.id,
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
        }
    });
});
