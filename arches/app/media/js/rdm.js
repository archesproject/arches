require([
    'jquery',
    'arches',
    'jquery-validate',
    'plugins/jqtree/tree.jquery'
], function($, arches) {
    $(document).ready(function() {
        var _selectedConcept = $('#selected-conceptid').val(),
            tree = $('#jqtree').tree({
                dragAndDrop: true,
                dataUrl: arches.urls.concept_tree + (_selectedConcept === '' ? '' : "?node=" + _selectedConcept),
                data: [],
                autoOpen: true
            }),
            labelEditor = $('#labelmodal'),
            noteEditor = $('#notemodal'),
            relatedValueEditor = $('#related_valuemodal'),
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
                    }
                });
            },
            getSelectedConcept = function() {
                //return tree.tree('getSelectedNode');
                return _selectedConcept;
            },
            setSelectedConcept = function(conceptid) {
                var node = tree.tree('getNodeById', conceptid);
                if (node) {
                    // collapse the node while it's loading
                    if (!node.load_on_demand) {
                        tree.tree('toggle', node);
                    }
                    $(node.element).addClass('jqtree-loading');
                }

                if (conceptid !== '') {
                    _selectedConcept = conceptid;
                    window.history.pushState({}, "conceptid", conceptid);
                    loadConceptReport(conceptid);
                }

                tree.tree(
                    'loadDataFromUrl',
                    arches.urls.concept_tree + "?node=" + conceptid,
                    null,
                    function() {
                        data_tree = tree.tree('getTree');
                        var conceptid = getSelectedConcept()
                        if (conceptid === '') {
                            // get the top level concept from the tree
                            conceptid = data_tree.children[0].id;
                            _selectedConcept = conceptid;
                            window.history.pushState({}, "conceptid", conceptid);
                            loadConceptReport(conceptid);
                        }

                        var node = tree.tree('getNodeById', conceptid);
                        tree.tree('selectNode', node);
                        tree.tree('scrollToNode', node);
                    }
                );
            },
            saveValue = function(data, successCallback, errorCallback) {
                $.ajax({
                    type: "POST",
                    url: arches.urls.concept_value,
                    data: {
                        'json': JSON.stringify(data)
                    },
                    success: successCallback,
                    error: errorCallback
                });
            },
            deleteValue = function(valueid, successCallback, errorCallback) {
                $.ajax({
                    type: "DELETE",
                    url: arches.urls.concept_value + valueid,
                    success: successCallback,
                    error: errorCallback
                });
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
                console.log('moved_node', event.move_info.moved_node);
                console.log('target_node', event.move_info.target_node);
                console.log('position', event.move_info.position); // possible values: inside, before, after
                console.log('previous_parent', event.move_info.previous_parent);

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

                                if (getSelectedConcept() === data.conceptid) {
                                    reloadReport();
                                }
                            },
                            error: errorCallback
                        });
                    }
                }
            },
            reloadReport = function() {
                loadConceptReport(getSelectedConcept());
            },
            reloadConcept = function() {
                setSelectedConcept(getSelectedConcept());
            };

        setSelectedConcept(_selectedConcept);

        // bind 'tree.click' event
        tree.bind(
            'tree.click',
            function(event) {
                // The clicked node is 'event.node'
                var node = event.node;
                if (getSelectedConcept() !== node.id) {
                    setSelectedConcept(node.id);
                } else {
                    event.preventDefault();
                }
            }
        );

        // bind 'tree.click' event
        tree.bind(
            'tree.move',
            function(event) {
                moveConcept(event, function() {
                    event.move_info.do_move();
                }, function() {
                    alert('well that didn\'t work...');
                });
            }
        );

        // LABEL EDITOR
        labelEditor.on('show.bs.modal', function(e) {
            var data = $(e.relatedTarget).data();
            if (data.action === 'edit') {
                $('#labelmodaltitle').text('Edit Label');
                $('#label_value').val(data.label_value);
                $('#label_id').val(data.label_id);
                $('#label_valuetype_dd').select2("val", data.label_type);
                $('#label_language_dd').select2("val", data.label_language);
            }

            if (data.action === 'add') {
                $('#labelmodaltitle').text('Add New Label');
                $('#label_value').val('');
                $('#label_id').val('');
                $('#label_valuetype_dd').select2("val", '');
                //$('#label_language_dd').select2("val", '');
            }
        });
        labelEditor.validate({
            ignore: null, // required so that the select2 dropdowns will be visible to the validate plugin
            rules: {
                // element_name: value
                label_value: "required",
                label_valuetype_dd: "required",
                label_language_dd: "required"
            },
            submitHandler: function(form) {
                var data = {};
                data.value = $('#label_value').val();
                data.id = $('#label_id').val();
                data.conceptid = getSelectedConcept();
                data.valuetype = $('#label_valuetype_dd').select2('val');
                data.datatype = 'text';
                data.language = $('#label_language_dd').select2('val');

                saveValue(data, function(data) {
                    labelEditor.modal('hide');
                    reloadConcept();
                }, null);
            }
        });


        // NOTE EDITOR 
        noteEditor.on('show.bs.modal', function(e) {
            var data = $(e.relatedTarget).data();
            if (data.action === 'edit') {
                $('#notemodaltitle').text('Edit Note');
                $('#note_value').val(data.note_value);
                $('#note_id').val(data.note_id);
                $('#note_valuetype_dd').select2("val", data.note_type);
                $('#note_language_dd').select2("val", data.note_language);
            }

            if (data.action === 'add') {
                $('#notemodaltitle').text('Add New Note');
                $('#note_value').val('');
                $('#note_id').val('');
                $('#note_valuetype_dd').select2("val", '');
                //$('#note_language_dd').select2("val", '');
            }
        });
        noteEditor.validate({
            ignore: null, // required so that the select2 dropdowns will be visible to the validate plugin
            rules: {
                // element_name: value
                note_value: "required",
                note_valuetype_dd: "required",
                note_language_dd: "required"
            },
            submitHandler: function(form) {
                var data = {};
                data.value = $('#note_value').val();
                data.id = $('#note_id').val();
                data.conceptid = getSelectedConcept();
                data.valuetype = $('#note_valuetype_dd').select2('val');
                data.datatype = 'text';
                data.language = $('#note_language_dd').select2('val');

                saveValue(data, function(data) {
                    noteEditor.modal('hide');
                    reloadReport();
                }, null);
            }
        });

        // RELATED VALUE EDITOR 
        relatedValueEditor.on('show.bs.modal', function(e) {
            var data = $(e.relatedTarget).data();
            if (data.action === 'edit') {
                $('#related_valuemodaltitle').text('Edit Related Value');
                $('#related_value_value').val(data.related_value_value);
                $('#related_value_id').val(data.related_value_id);
                $('#related_value_valuetype_dd').select2("val", data.related_value_type);
                $('#related_value_language_dd').select2("val", data.related_value_language);
            }

            if (data.action === 'add') {
                $('#related_valuemodaltitle').text('Add Related Value');
                $('#related_value_value').val('');
                $('#related_value_id').val('');
                $('#related_value_valuetype_dd').select2("val", '');
                //$('#related_value_language_dd').select2("val", '');
            }
        });
        relatedValueEditor.validate({
            ignore: null, // required so that the select2 dropdowns will be visible to the validate plugin
            rules: {
                // element_name: value
                related_value_value: "required",
                related_value_valuetype_dd: "required",
                related_value_language_dd: "required"
            },
            submitHandler: function(form) {
                var data = {};
                data.value = $('#related_value_value').val();
                data.id = $('#related_value_id').val();
                data.conceptid = getSelectedConcept();
                data.valuetype = $('#related_value_valuetype_dd').select2('val');
                data.datatype = 'text';
                data.language = $('#related_value_language_dd').select2('val');

                saveValue(data, function(data) {
                    relatedValueEditor.modal('hide');
                    reloadReport();
                }, null);
            }
        });

        // ADD CHILD CONCEPT EDITOR 
        conceptEditor.validate({
            ignore: null, // required so that the select2 dropdowns will be visible to the validate plugin
            rules: {
                // element_name: value
                label: "required",
                language_dd: "required"
            },
            submitHandler: function(form) {
                var data = {};
                data.label = $(form).find("[name=label]").val();
                data.note = $(form).find("[name=note]").val();
                data.language = $(form).find("[name=language_dd]").select2('val');
                data.parentconceptid = getSelectedConcept();

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
                deleteValue(data.id, function(data) {
                    $('#confirm_delete_modal').modal('hide');
                    reloadReport();
                }, null);
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