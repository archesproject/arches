define([
    'knockout',
    'knockout-mapping',
    'underscore',
    'arches',
    'dropzone',
    'uuid',
    'viewmodels/card-component',
    'views/components/workbench',
    'file-renderers',
    'bindings/slide',
    'bindings/fadeVisible',
    'bindings/dropzone'
], function(ko, koMapping, _, arches, Dropzone, uuid, CardComponentViewModel, WorkbenchComponentViewModel, fileRenderers) {
    return ko.components.register('file-viewer', {
        viewModel: function(params) {
            params.configKeys = ['acceptedFiles', 'maxFilesize'];
            var self = this;
            this.fileFormatRenderers = fileRenderers;
            this.fileFormatRenderers.forEach(function(r){
                r.state = {};
            });
            CardComponentViewModel.apply(this, [params]);
            WorkbenchComponentViewModel.apply(this, [params]);
            if (this.card && this.card.activeTab) {
                self.activeTab(this.card.activeTab);
            } else {
                self.activeTab = ko.observable();
            }

            this.selected = ko.observable();
            self.activeTab.subscribe(
                function(val){
                    self.card.activeTab = val;
                });

            self.card.tiles.subscribe(function(val){
                if (val.length === 0) {
                    self.activeTab(null);
                }
            });

            this.getUrl = function(tile){
                var url = '';
                var type = '';
                _.each(tile.data,
                    function(v, k) {
                        var val = ko.unwrap(v);
                        if (Array.isArray(val)
                            && val.length == 1
                            && (ko.unwrap(val[0].url) || ko.unwrap(val[0].content))) {
                            url = ko.unwrap(val[0].url) || ko.unwrap(val[0].content);
                            type = ko.unwrap(val[0].type);
                            name = ko.unwrap(val[0].name);
                        }
                    });
                return {url: url, type: type, name: name};
            };

            this.uniqueId = uuid.generate();
            this.uniqueidClass = ko.computed(function() {
                return "unique_id_" + self.uniqueId;
            });

            this.showThumbnails = ko.observable(false);

            this.selectDefault = function(){
                var self = this;
                return function() {
                    var selectedIndex = self.card.tiles.indexOf(self.selected());
                    if(self.card.tiles().length > 0 && selectedIndex === -1) {
                        selectedIndex = 0;
                    }
                    self.card.tiles()[selectedIndex];
                };
            };

            this.defaultSelector = this.selectDefault();

            this.displayContent = ko.pureComputed(function(){
                var file;
                var selected = this.card.tiles().find(
                    function(tile){
                        return tile.selected() === true;
                    });
                if (selected) {
                    this.selected(selected);
                    file = this.getUrl(selected);
                }
                else {
                    this.selected(undefined);
                }
                return file;
            }, this);

            if (this.displayContent() === undefined) {
                var selectedIndex = 0;
                if (
                    this.card.tiles().length > 0 &&
                    this.form &&
                    (ko.unwrap(this.form.selection) && this.form.selection() !== 'root') ||
                    (this.form && !ko.unwrap(this.form.selection))) {
                }
                this.activeTab(undefined);
            }

            this.selectItem = function(val){
                if (val && val.selected) {
                    if (ko.unwrap(val) !== true) {
                        val.selected(true);
                    }
                }
            }

            this.removeTile = function(val){
                //TODO: Upon deletion select the tile to the left of the deleted tile
                //If the deleted tile is the first tile, then select the tile to the right
                // var tileCount = this.parent.tiles().length;
                // var index = this.parent.tiles.indexOf(val);
                val.deleteTile();
                setTimeout(self.defaultSelector, 150);
            };

            this.typeMatch = function(type){
                var rawFileType = ko.unwrap(self.displayContent).type;
                if (type === rawFileType) {
                    return true;
                }
                var splitFileType = ko.unwrap(self.displayContent).type.split('/');
                var fileType = splitFileType[0];
                var splitAllowableType = type.split('/');
                var allowableType = splitAllowableType[0];
                var allowableSubType = splitAllowableType[1];
                if (allowableSubType === '*' && fileType === allowableType) {
                    return true;
                }
                return false;
            };

            this.addTile = function(file){
                var newtile;
                newtile = self.card.getNewTile();
                var targetNode;
                var tilevalue = {
                    name: file.name,
                    accepted: true,
                    height: file.height,
                    lastModified: file.lastModified,
                    size: file.size,
                    status: file.status,
                    type: file.type,
                    width: file.width,
                    url: null,
                    file_id: null,
                    index: 0,
                    content: URL.createObjectURL(file),
                    error: file.error
                };
                Object.keys(newtile.data).forEach(function(val){
                    if (newtile.datatypeLookup && newtile.datatypeLookup[val] === 'file-list') {
                        targetNode = val;
                    }
                });
                newtile.data[targetNode]([tilevalue]);
                newtile.formData.append('file-list_' + targetNode, file, file.name);
                newtile.save();
                self.card.newTile = undefined;
            };

            this.dropzoneOptions = {
                url: "arches.urls.root",
                dictDefaultMessage: '',
                autoProcessQueue: false,
                uploadMultiple: true,
                autoQueue: false,
                clickable: ".fileinput-button." + this.uniqueidClass(),
                previewsContainer: '#hidden-dz-previews',
                init: function() {
                    self.dropzone = this;
                    this.on("addedfile", self.addTile, self);
                    this.on("error", function(file, error) {
                        file.error = error;
                    });
                }
            };
        },
        template: {
            require: 'text!templates/views/components/cards/file-viewer.htm'
        }
    });
});
