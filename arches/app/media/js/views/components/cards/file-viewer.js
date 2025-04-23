import $ from 'jquery';
import ko from 'knockout';
import uuid from 'uuid';
import arches from 'arches';
import fileRenderers from 'file-renderers';
import CardComponentViewModel from 'viewmodels/card-component';
import CardMultiSelectViewModel from 'viewmodels/card-multi-select';
import WorkbenchComponentViewModel from 'views/components/workbench';
import fileViewerTemplate from 'templates/views/components/cards/file-viewer.htm';
import 'bindings/slide';
import 'bindings/fadeVisible';
import 'bindings/scroll-to-file';
import 'dropzone';
import 'bindings/dropzone';


const viewModel = function(params) {
    params.configKeys = ['acceptedFiles', 'maxFilesize'];

    var self = this;
    this.urls = arches.urls;
        
    this.fileFormatRenderers = Object.values(fileRenderers);
    this.rendererComponentName = ko.observable();

    this.fileFormatRenderers.forEach(function(r){
        r.state = {};
        r.disabled = true;
    });

    this.applyToAll = ko.observable(false);

    CardComponentViewModel.apply(this, [params]);

    if (!this.card.staging) {
        CardMultiSelectViewModel.apply(this, [params]);
    } else {
        this.card.staging.valueHasMutated();
    }
    
    if ('filter' in this.card === false) {
        this.card.filter = ko.observable('');
    }
    if ('renderer' in this.card === false) {
        this.card.renderer = ko.observable();
    }

    this.fileRenderer = this.card.renderer;

    //dynamically require the renderer - since these can be quite large/cumbersome
    const renderer = fileRenderers[ko.unwrap(this.fileRenderer.id || this.fileRenderer)];

    if(renderer){
        self.rendererComponentName(renderer.name);
    }

    this.managerRenderer = ko.observable();

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
    this.acceptedFiles = ko.observable(null);

    this.displayWidgetIndex = self.card.widgets().indexOf(self.card.widgets().find(function(widget) {
        return widget.datatype.datatype === 'file-list';
    }));

    WorkbenchComponentViewModel.apply(this, [params]);
    this.workbenchWrapperClass = ko.observable('autoheight');

    if (this.card && this.card.activeTab) {
        self.activeTab(this.card.activeTab);
    } else {
        self.activeTab = ko.observable();
    }

    this.selected = ko.observable();

    this.activeTab.subscribe(
        function(val){
            self.card.activeTab = val;
        });

    this.fileRenderer.subscribe(function(){
        if (['add', 'edit', 'manage'].indexOf(self.activeTab()) < 0) {
            self.activeTab(undefined);
        }
    });

    self.card.tiles.subscribe(function(val){
        if (val.length === 0) {
            self.activeTab(null);
        }
    });

    this.getFileFormatRenderer = function(rendererid) {
        return self.fileFormatRenderers.find(function(item) {
            return item.id === rendererid;
        });
    };
    
    if (!this.card.checkrenderers) {
        this.card.checkrenderers = this.card.staging.subscribe(function(){
            var compatible = [];
            var compatibleIds = [];
            var allCompatible = true;
            var staging = self.card ? self.card.staging() : [];
            var staged = self.card.tiles().filter(function(tile){
                return staging.indexOf(tile.tileid) >= 0;  
            });
            staged.forEach(function(tile){
                var file = tile.data[self.fileListNodeId]()[0];
                var defaultRenderers = self.getDefaultRenderers(ko.unwrap(file.type), ko.unwrap(file.name));
                if (compatible.length === 0) {
                    compatible = defaultRenderers;
                    compatibleIds = compatible.map(function(x){return x.id;});
                } else {
                    allCompatible = defaultRenderers.every(function(renderer){
                        return compatibleIds.indexOf(renderer.id) > -1;
                    }); 
                }
            });
            self.fileFormatRenderers.forEach(function(r){
                if (compatibleIds.indexOf(r.id) === -1 || allCompatible === false) {
                    r.disabled = true;
                } else {
                    r.disabled = false;
                }
            });
        });
    }

    this.getDefaultRenderers = function(type, file){
        var defaultRenderers = [];
        this.fileFormatRenderers.forEach(function(renderer){
            var excludeExtensions = renderer.exclude ? renderer.exclude.split(",") : [];
            var rawFileType = type;
            try {
                rawExtension = ko.unwrap(file).split('.').pop();
            } catch (error) {
                var rawExtension = file.name ? ko.unwrap(file.name).split('.').pop() : undefined;
            }
            if (renderer.type === rawFileType && renderer.ext === rawExtension)  {
                defaultRenderers.push(renderer);
            }
            var splitFileType = ko.unwrap(type).split('/');
            var fileType = splitFileType[0];
            var splitAllowableType = renderer.type.split('/');
            var allowableType = splitAllowableType[0];
            var allowableSubType = splitAllowableType[1];
            if (allowableSubType === '*' && fileType === allowableType && excludeExtensions.indexOf(rawExtension) < 0) {
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

    this.isFiltered = function(t){
        return self.getUrl(t).name.toLowerCase().includes(self.filter().toLowerCase());
    };

    this.filteredTiles = ko.pureComputed(function(){
        return self.card.tiles().filter(function(t){
            return self.getUrl(t).name.toLowerCase().includes(self.filter().toLowerCase());
        }, this);
    }, this);

    this.uniqueId = uuid.generate();
    this.uniqueidClass = ko.computed(function() {
        return "unique_id_" + self.uniqueId;
    });

    this.selectDefault = function(){
        var self = this;
        return function() {
            var t;
            var openTab = self.activeTab() === 'manage' ? 'manage' : 'edit'; 
            self.toggleTab(openTab);
            var selectedIndex = self.card.tiles.indexOf(self.selected());
            if(self.card.tiles().length > 0 && selectedIndex === -1) {
                selectedIndex = 0;
            }
            t = self.card.tiles()[selectedIndex];
            if(t) {
                t.selected(true);
                self.selectItem(t);
            }
            self.activeTab(openTab);
        };
    };
    this.defaultSelector = this.selectDefault();

    this.checkIfRendererIsValid = function(file, renderer){
        var defaultRenderers = self.getDefaultRenderers(ko.unwrap(file.type), ko.unwrap(file.name));
        return (defaultRenderers.indexOf(renderer) > -1);
    };

    this.applyRendererToStaged = function(renderer) {
        this.card.staging().forEach(function(tileid){
            var stagedTile = self.card.tiles().find(function(t){return t.tileid == tileid;});
            if (stagedTile) {
                var node = ko.unwrap(stagedTile.data[self.fileListNodeId]);
                var file = node[0];
                var valid = self.checkIfRendererIsValid(file, renderer);
                if (valid) {
                    file.renderer = renderer ? renderer.id : '';
                    stagedTile.save();
                }
            }
        });
    }; 

    this.applyRendererToSelected = function(renderer){	
        if (self.displayContent()) {	
            var tile = self.displayContent().tile;	
            var node = ko.unwrap(tile.data[self.fileListNodeId]);	
            if (node.length > 0) {	
                var valid = self.checkIfRendererIsValid(node[0], renderer);	
                if (valid) {	
                    node[0].renderer = renderer ? renderer.id : '';	
                    tile.save();	
                }	
            }	
        } if (ko.unwrap(self.applyToAll)) {
            self.applyRendererToStaged(renderer);
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
            if (['add', 'edit', 'manage'].indexOf(self.activeTab()) < 0) {
                self.activeTab(undefined);
            }
        }
        if (file) {
            file.availableRenderers = self.getDefaultRenderers(file.type, file);
            file.validRenderer = ko.observable(true);
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

    this.removeTiles = function() {
        this.card.staging().forEach(function(tileid){
            var stagedTile = self.card.tiles().find(function(t){return t.tileid == tileid;});
            if (stagedTile) {
                stagedTile.deleteTile(null, self.defaultSelector);
            }
        }, this);
        self.card.staging([]);
    };  
    
    this.stageAll = function() {
        this.card.tiles().forEach(function(tile){
            if (self.card.staging().indexOf(tile.tileid) < 0) {
                self.card.staging.push(tile.tileid);
            }
        });
    };

    this.stageFiltered = function() {
        self.card.staging([]);
        this.filteredTiles().forEach(function(tile){
            if (self.card.staging().indexOf(tile.tileid) < 0) {
                self.card.staging.push(tile.tileid);
            }
        });
    };

    this.clearStaging = function() {
        self.card.staging([]);
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

    function stageTile(t) {
        self.card.staging.push(t.tileid);
    }

    this.downloadSelection = function() {
        var url = arches.urls.download_files + "?tiles=" + JSON.stringify(self.card.staging()) + "&node=" + self.fileListNodeId;
        window.open(url);
    };

    this.addTile = function(file){
        var newtile;
        newtile = self.card.getNewTile();
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
        newtile.data[self.fileListNodeId]([tilevalue]);
        newtile.formData.append('file-list_' + self.fileListNodeId, file, file.name);
        newtile.resourceinstance_id = self.card.resourceinstanceid;
        if (self.card.tiles().length === 0) {
            sleep(100);
        }
        newtile.save(null, stageTile);
        self.card.newTile = undefined;
    };

    this.getAcceptedFiles = function(){
        self.card.widgets().forEach(function(w) {
            if (w.node_id() === self.fileListNodeId) {
                if (ko.unwrap(w.attributes.config.acceptedFiles)) {
                    self.acceptedFiles(ko.unwrap(w.attributes.config.acceptedFiles));
                }
            }
        });
    };
    this.getAcceptedFiles();

    this.dropzoneOptions = {
        url: "arches.urls.root",
        dictDefaultMessage: '',
        autoProcessQueue: false,
        uploadMultiple: true,
        autoQueue: false,
        acceptedFiles: self.acceptedFiles(),
        clickable: ".fileinput-button." + this.uniqueidClass(),
        previewsContainer: '#hidden-dz-previews',
        init: function() {
            self.dropzone = this;
            this.on("addedfiles", function() {
                self.card.staging([]);
            });
            this.on("addedfile", self.addTile, self);
            this.on("error", function(file, error) {
                file.error = error;
            });
        }
    };
};

export default ko.components.register('file-viewer', {
    viewModel: viewModel,
    template: fileViewerTemplate,
});
