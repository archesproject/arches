require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/search-base-manager',
    'views/resource/editor/form-list',
    'viewmodels/provisional-tile',
    'views/resource/editor/form',
    'models/card',
    'viewmodels/alert',
    'resource-editor-data',
    'bindings/sortable',
    'bindings/let'
], function($, _, ko, arches, SearchBaseManagerView, FormList, ProvisionalTileViewModel, FormView, CardModel, AlertViewModel, data) {
    var self = this;
    var loading = ko.observable(false);
    var cardLoading = ko.observable(false);
    var provisionalLoading = ko.observable(false);
    var selectedForm = ko.observable();
    var displayName = ko.observable(data.displayName);
    var resourceInstanceExists = ko.observable(data.resourceInstanceExists === "True" || false)
    var formList = new FormList({
        forms: ko.observableArray(data.forms)
    });
    formList.selectItem(formList.items()[0]);

    var selectedProvisionalTile = ko.observable()

    var provisionalTileViewModel = new ProvisionalTileViewModel(
        {
            selectedProvisionalTile: selectedProvisionalTile,
            cardModel: CardModel,
            selectedForm: selectedForm,
            loading: provisionalLoading
        }
    );

    var formView = new FormView({
        formid: formList.items()[0].formid,
        resourceid: data.resourceid,
        tiles: data.tiles,
        blanks: data.blanks,
        resourceexists: resourceInstanceExists,
        selectedProvisionalTile: selectedProvisionalTile,
        provisionalTileViewModel: provisionalTileViewModel
    });

    var loadForm = function(form) {
        cardLoading(true);
        selectedForm(form.formid)
        formView.loadForm(form.formid, function(){
            cardLoading(false);
        });
    };

    formList.on('item-clicked', function(form){
        if (pageView.viewModel.dirty()) {
            pageView.viewModel.alert(new AlertViewModel('ep-alert-blue', arches.confirmNav.title, arches.confirmNav.text, function(){
                pageView.viewModel.showConfirmNav(false);
            }, function() {
                loadForm(form);
            }));
        } else {
            loadForm(form);
        }
    });

    formView.on('before-update', function(){
        cardLoading(true);
    });

    formView.on('after-update', function(response){
        cardLoading(false);
        var updateDisplayName = function(){
            var name = displayName;
            return function(val) {
                name(val.displayname)
            }
        }
        var errorMessageTitle = arches.requestFailed.title
        var errorMessageText = arches.requestFailed.text
        pageView.viewModel.alert(null);
        if(response.status != 200){
            if (response.responseJSON) {
              errorMessageTitle = response.responseJSON.message[0]
              errorMessageText = response.responseJSON.message[1]
            }
            pageView.viewModel.alert(new AlertViewModel('ep-alert-red', errorMessageTitle, errorMessageText));
        } else {
            $.get(arches.urls.resource_descriptors + this.resourceid, updateDisplayName());
        }
    });

    /**
    * a PageView representing the resource listing and recent edits page
    */
    var pageView = new SearchBaseManagerView({
        viewModel:{
            loading: loading,
            loadingSearch: ko.observable(false),
            cardLoading: cardLoading,
            provisionalLoading: provisionalLoading,
            displayName: displayName,
            resourceEditorContext: true,
            resourceInstanceExists: resourceInstanceExists,
            editingInstanceId: data.resourceid,
            relationship_types: data.relationship_types,
            graph: data.graph,
            formList: formList,
            provisionalTileViewModel: provisionalTileViewModel,
            formView: formView,
            openRelatedResources: ko.observable(false),
            rrLoaded: ko.observable(false),
            dirty: ko.computed(function() {
                var dirty = false;
                _.each(formView.formTiles(), function (tile) {
                    if (tile.dirty()) {
                        dirty = true;
                    }
                });
                return dirty;
            }),
            deleteResource: function(){
                pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmResourceDelete.title, arches.confirmResourceDelete.text, function() {
                    return;
                }, function(){
                    loading(true);
                    $.ajax({
                        type: "DELETE",
                        url: arches.urls.resource_editor + data.resourceid,
                        success: function(response) {

                        },
                        error: function(response) {

                        },
                        complete: function (request, status) {
                            loading(false);
                            if (status === 'success') {
                                pageView.viewModel.navigate(arches.urls.resource);
                            }
                        },
                    });
                }));
            },
            copyResource: function(){
                loading(true);
                $.ajax({
                    type: "GET",
                    url: arches.urls.resource_copy.replace('//', '/' + data.resourceid + '/'),
                    success: function(response) {
                        pageView.viewModel.alert(new AlertViewModel('ep-alert-blue', arches.resourceCopySuccess.title, '', null, function(){}));
                    },
                    error: function(response) {
                        pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.resourceCopyFailed.title, arches.resourceCopyFailed.text, null, function(){}));
                    },
                    complete: function (request, status) {
                        loading(false);
                    },
                });
            },
            renderSearch: function() {
                var self = this;
                var el = $('.related-resources-editor-container');
                self.loadingSearch(true);
                $.ajax({
                    type: "GET",
                    url: arches.urls.resource_editor + data.resourceid,
                    data: {'search': true, 'csrfmiddlewaretoken': '{{ csrf_token }}'},
                    success : function(data) {
                         self.loadingSearch(false);
                         el.html(data);
                         ko.applyBindings(self, el[0]);
                     }
                });
            }
        }
    });

    pageView.viewModel.openRelatedResources.subscribe(function(val){
        if (pageView.viewModel.rrLoaded() === false) {
            pageView.viewModel.rrLoaded(true)
            pageView.viewModel.renderSearch()
        }
    })

    pageView.viewModel.searchResults.relationshipCandidates.subscribe(function () {
        if (!pageView.viewModel.openRelatedResources()) {
            pageView.viewModel.openRelatedResources(true);
        }
        if (pageView.viewModel.selectedTab() !== pageView.viewModel.relatedResourcesManager) {
            pageView.viewModel.selectedTab(pageView.viewModel.relatedResourcesManager);
        }
    });
});
