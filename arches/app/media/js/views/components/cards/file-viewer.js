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
            this.filter = ko.observable('');
            this.fileFormatRenderers.forEach(function(r){
                r.state = {};
            });
            this.fileRenderer = ko.observable();

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

            this.isFiltered = function(t){
                return self.getUrl(t).name.toLowerCase().includes(self.filter().toLowerCase());
            };

            this.getDefaultRenderer = function(type, file){
                var defaultRenderer = '';
                this.fileFormatRenderers.forEach(function(renderer){
                    var rawFileType = type;
                    var rawExtension = file.url ? ko.unwrap(file.url).split('.').pop() : file.split('.').pop();
                    if (renderer.type === rawFileType && renderer.ext === rawExtension)  {
                        defaultRenderer = renderer;
                    }
                    var splitFileType = type.split('/');
                    var fileType = splitFileType[0];
                    var splitAllowableType = renderer.type.split('/');
                    var allowableType = splitAllowableType[0];
                    var allowableSubType = splitAllowableType[1];
                    if (allowableSubType === '*' && fileType === allowableType) {
                        defaultRenderer = renderer;
                    }
                }); 

                return defaultRenderer;
            };

            this.getUrl = function(tile){
                var url = '';
                var type = '';
                var name;
                var renderer;
                var iconclass;
                var rendererid;
                _.each(tile.data,
                    function(v, k) {
                        var val = ko.unwrap(v);
                        if (Array.isArray(val)
                            && val.length == 1
                            && (ko.unwrap(val[0].url) || ko.unwrap(val[0].content))) {
                            url = ko.unwrap(val[0].url) || ko.unwrap(val[0].content);
                            type = ko.unwrap(val[0].type);
                            name = ko.unwrap(val[0].name);
                            rendererid = ko.unwrap(val[0].renderer);
                            renderer = self.fileFormatRenderers.find(function(item) {
                                return item.id === rendererid;
                            });
                            if (renderer) {
                                iconclass = renderer.iconclass;
                            } else {
                                renderer = self.getDefaultRenderer(type, val[0]);
                                if (renderer) {
                                    renderer = self.getDefaultRenderer(type, val[0].name());
                                    iconclass = renderer.iconclass;
                                }
                            }
                        }
                    });
                return {url: url, type: type, name: name, renderer: renderer, iconclass: iconclass};
            };

            this.uniqueId = uuid.generate();
            this.uniqueidClass = ko.computed(function() {
                return "unique_id_" + self.uniqueId;
            });

            this.selectDefault = function(){
                var self = this;
                return function() {
                    var t;
                    self.toggleTab('edit');
                    self.activeTab('edit');
                    var selectedIndex = self.card.tiles.indexOf(self.selected());
                    if(self.card.tiles().length > 0 && selectedIndex === -1) {
                        selectedIndex = 0;
                    }
                    t = self.card.tiles()[selectedIndex];
                    if(t) {
                        t.selected(true);
                        self.selectItem(t);
                    }
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
                    if (!this.selected() || (this.selected() && this.selected().tileid !== selected.tileid)) {
                        this.selected(selected);
                    }
                    file = this.getUrl(selected);
                    this.fileRenderer(file.renderer ? file.renderer.id : undefined)
                }
                else {
                    this.selected(undefined);
                    if (['add', 'edit'].indexOf(self.activeTab()) < 0) {
                        self.activeTab(undefined);
                    }
                }
                return file;
            }, this);

            if (this.displayContent() === undefined) {
                this.activeTab(undefined);
            }

            this.selectItem = function(val){
                if (val && val.selected) {
                    if (ko.unwrap(val) !== true && ko.unwrap(val.selected) !== true) {
                        val.selected(true);
                    }
                }
            };

            this.removeTile = function(val){
                val.deleteTile(null, self.defaultSelector);
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
                    content: window.URL.createObjectURL(file),
                    error: file.error,
                    renderer: self.getDefaultRenderer(file.type, file.name).id
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
