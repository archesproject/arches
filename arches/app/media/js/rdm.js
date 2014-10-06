require([
    'jquery',
    'arches',
    'models/value',
    'views/value-editor',
    'jquery-validate',
    'plugins/jqtree/tree.jquery'
], function($, arches, ValueModel, ValueEditor) {
    $(document).ready(function() {
        var selectedConcept = '',
            conceptTree = $('#jqtree').tree({
                dragAndDrop: true,
                dataUrl: arches.urls.concept_tree + (selectedConcept === '' ? '' : "?node=" + selectedConcept),
                data: [],
                autoOpen: true
            }),
            conceptEditor = $('#conceptmodal'),
            loadConceptReport = function(conceptid) {
                $('#concept_report_loading').removeClass('hidden');
                $('#concept_report').addClass('hidden');
                $.ajax({
                    url: '../Concepts/' + conceptid + '?f=html',
                    success: function(response) {
                        $('#concept_report_loading').addClass('hidden');
                        $('#concept_report').removeClass('hidden');
                        $('#concept_report').html(response);
                        $('.edit-value').click(function (e) {
                            var data = $.extend({conceptid: selectedConcept}, $(e.target).data()),
                                model = new ValueModel(data),
                                editor = new ValueEditor({
                                    el: $(data.target)[0],
                                    model: model
                                });

                            editor.on('submit', function () {
                                model.save(reloadConcept);
                            });
                        });
                    }
                });
            },
            setSelectedConcept = function(conceptid) {
                var node = conceptTree.tree('getNodeById', conceptid);
                if (node) {
                    // collapse the node while it's loading
                    if (!node.load_on_demand) {
                        conceptTree.tree('toggle', node);
                    }
                    $(node.element).addClass('jqtree-loading');
                }

                if (conceptid !== '') {
                    selectedConcept = conceptid;
                    window.history.pushState({}, "conceptid", conceptid);
                    loadConceptReport(conceptid);
                }

                conceptTree.tree(
                    'loadDataFromUrl',
                    arches.urls.concept_tree + "?node=" + conceptid,
                    null,
                    function() {
                        var dataTree = conceptTree.tree('getTree');
                        if (selectedConcept === '') {
                            // get the top level concept from the tree
                            selectedConcept = dataTree.children[0].id;
                            window.history.pushState({}, "conceptid", selectedConcept);
                            loadConceptReport(selectedConcept);
                        }

                        var node = conceptTree.tree('getNodeById', selectedConcept);
                        conceptTree.tree('selectNode', node);
                        conceptTree.tree('scrollToNode', node);
                    }
                );
            },
            addConcept = function(data, successCallback, errorCallback) {
                $.ajax({
                    type: "POST",
                    url: arches.urls.concept,
                    data: JSON.stringify(data),
                    success: successCallback,
                    error: errorCallback
                });
            },
            deleteConcept = function(data, successCallback, errorCallback) {
                $.ajax({
                    type: "DELETE",
                    url: arches.urls.concept + data,
                    success: successCallback,
                    error: errorCallback
                });
            },
            moveConcept = function(event, successCallback, errorCallback) {
                var move_info = event.move_info;
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
                                successCallback();
                                var data = JSON.parse(this.data);

                                if (selectedConcept === data.conceptid) {
                                    reloadReport();
                                }
                            },
                            error: errorCallback
                        });
                    }
                }
            },
            reloadReport = function() {
                loadConceptReport(selectedConcept);
            },
            reloadConcept = function() {
                setSelectedConcept(selectedConcept);
            };

        setSelectedConcept($('#selected-conceptid').val());

        // bind 'tree.click' event
        conceptTree.bind(
            'tree.click',
            function(event) {
                // The clicked node is 'event.node'
                var node = event.node;
                if (selectedConcept !== node.id) {
                    setSelectedConcept(node.id);
                } else {
                    event.preventDefault();
                }
            }
        );

        // bind 'tree.click' event
        conceptTree.bind(
            'tree.move',
            function(event) {
                moveConcept(event, function() {
                    event.move_info.do_move();
                });
            }
        );

        // ADD CHILD CONCEPT EDITOR 
        conceptEditor.validate({
            ignore: null, // required so that the select2 dropdowns will be visible to the validate plugin
            rules: {
                // element_name: value
                label: "required",
                language_dd: "required"
            },
            submitHandler: function(form) {
                var data = {
                    label: $(form).find("[name=label]").val(),
                    note: $(form).find("[name=note]").val(),
                    language: $(form).find("[name=language_dd]").select2('val'),
                    parentconceptid: selectedConcept
                };

                addConcept(data, function(data) {
                    conceptEditor.modal('hide');
                    reloadConcept();
                }, null);
            }
        });

        // CLICK LISTENER 
        $(document).on('click', '#concept_report a', function() {
            var data = $(this).data();
            if (data.action === 'delete' || data.action === 'delete_concept') {
                $('#confirm_delete_modal .modal-title').text($(this).attr('title'));
                $('#confirm_delete_modal .modal-body').text(data.message);
                $('#confirm_delete_modal').modal('show');
                $('#confirm_delete_yes').data('id', data.id);
                $('#confirm_delete_yes').data('action', data.action);
            }

            if (data.action === 'viewconcept') {
                setSelectedConcept(data.conceptid);
            }
        });
        $('#confirm_delete_yes').on('click', function() {
            var data = $(this).data();
            if (data.action === 'delete') {
                var model = new ValueModel(data);
                model.delete(function () {
                    $('#confirm_delete_modal').modal('hide');
                    reloadReport();
                });
            }
            if (data.action === 'delete_concept') {
                deleteConcept(data.id, function(data) {
                    $('#confirm_delete_modal').modal('hide');
                    reloadConcept();
                }, null);
            }
        });
        $('#add_child_concept').on('click', function() {
            addConcept();
        });
    });
});