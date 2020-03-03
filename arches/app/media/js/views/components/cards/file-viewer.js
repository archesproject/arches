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
    'bindings/scroll-to-file',
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

            if ('filter' in this.card === false) {
                this.card.filter = ko.observable('');
            }
            if ('renderer' in this.card === false) {
                this.card.renderer = ko.observable();
            }

            this.fileRenderer = this.card.renderer;
            this.filter = this.card.filter;

            var getfileListNode = function(){
                var fileListNodeId;
                var fileListNodes = params.card.model.nodes().filter(
                    function(val){
                        if (val.datatype() === 'file-list' && self.card.nodegroupid == val.nodeGroupId())
                            return val;
                    });
                if (fileListNodes.length) {
                    fileListNodeId = fileListNodes[0].nodeid;
                }
                return fileListNodeId;
            };

            this.fileListNodeId = getfileListNode();

            this.displayWidgetIndex = self.card.widgets().indexOf(self.card.widgets().find(function(widget) {
                return widget.datatype.datatype === 'file-list';
            }));

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

            this.fileRenderer.subscribe(function(){
                if (['add', 'edit'].indexOf(self.activeTab()) < 0) {
                    self.activeTab(undefined);
                }
            });

            self.card.tiles.subscribe(function(val){
                if (val.length === 0) {
                    self.activeTab(null);
                }
            });

            this.isFiltered = function(t){
                return self.getUrl(t).name.toLowerCase().includes(self.filter().toLowerCase());
            };

            this.getDefaultRenderers = function(type, file){
                var defaultRenderers = [];
                this.fileFormatRenderers.forEach(function(renderer){
                    var rawFileType = type;
                    var rawExtension = file.url ? ko.unwrap(file.url).split('.').pop() : file.split('.').pop();
                    if (renderer.type === rawFileType && renderer.ext === rawExtension)  {
                        defaultRenderers.push(renderer);
                    }
                    var splitFileType = type.split('/');
                    var fileType = splitFileType[0];
                    var splitAllowableType = renderer.type.split('/');
                    var allowableType = splitAllowableType[0];
                    var allowableSubType = splitAllowableType[1];
                    if (allowableSubType === '*' && fileType === allowableType) {
                        defaultRenderers.push(renderer);
                    }
                }); 
                return defaultRenderers;
            };

            this.getUrl = function(tile){
                var url = '';
                var type = '';
                var name;
                var renderer;
                var iconclass;
                var rendererid;
                var availableRenderers;
                var val = ko.unwrap(tile.data[this.fileListNodeId]);
                if (val && val.length == 1) {
                    {
                        url = ko.unwrap(val[0].url) || ko.unwrap(val[0].content);
                        type = ko.unwrap(val[0].type);
                        name = ko.unwrap(val[0].name);
                        rendererid = ko.unwrap(val[0].renderer);
                        renderer = self.fileFormatRenderers.find(function(item) {
                            return item.id === rendererid;
                        });
                        if (!renderer) {
                            availableRenderers = self.getDefaultRenderers(type, val[0]);
                            if (!renderer) {
                                availableRenderers = self.getDefaultRenderers(type, ko.unwrap(val[0].name));
                            }
                        }
                        if (renderer) {
                            iconclass = renderer.iconclass;
                        }
                    }
                }
                return {url: url, type: type, name: name, renderer: renderer, iconclass: iconclass, tile: tile, renderers: availableRenderers};
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

            this.applyFileRenderer = function(val) {
                var tile = self.displayContent().tile;
                var node = ko.unwrap(tile.data[self.fileListNodeId]);
                if (node.length > 0) {
                    node[0].renderer = val.id;
                    tile.save();
                }
            }; 

            

            this.displayContent = ko.computed(function(){
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
                    this.fileRenderer(file.renderer ? file.renderer.id : undefined);
                }
                else {
                    this.selected(undefined);
                    if (['add', 'edit'].indexOf(self.activeTab()) < 0) {
                        self.activeTab(undefined);
                    }
                }
                if (file) {
                    file.availableRenderers = self.getDefaultRenderers(file.type, file);
                }
                return file;
            }, this).extend({deferred: true});

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

            if (this.form && ko.unwrap(this.form.resourceId)) {
                this.card.resourceinstanceid = ko.unwrap(this.form.resourceId);
            } else if (this.card.resourceinstanceid === undefined && this.card.tiles().length === 0) {
                this.card.resourceinstanceid = uuid.generate();
            }

            function sleep(milliseconds) {
                var start = new Date().getTime();
                for (var i = 0; i < 1e7; i++) {
                    if ((new Date().getTime() - start) > milliseconds){
                        break;
                    }
                }
            }

            this.addTile = function(file){
                var newtile;
                newtile = self.card.getNewTile();
                var targetNode;
                var defaultRenderers = self.getDefaultRenderers(file.type, file.name);
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
                    renderer: defaultRenderers.length === 1 ? defaultRenderers[0].id : undefined,
                };
                Object.keys(newtile.data).forEach(function(val){
                    if (newtile.datatypeLookup && newtile.datatypeLookup[val] === 'file-list') {
                        targetNode = val;
                    }
                });
                newtile.data[targetNode]([tilevalue]);
                newtile.formData.append('file-list_' + targetNode, file, file.name);
                newtile.resourceinstance_id = self.card.resourceinstanceid;
                if (self.card.tiles().length === 0) {
                    sleep(50);
                }
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
