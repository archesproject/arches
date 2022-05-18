define([
    'jquery',
    'knockout',
    'arches',
    'uuid',
    'viewmodels/card-component',
    'viewmodels/card-multi-select',
    'views/components/workbench',
    'file-renderers',
    'models/tile'
], function($, ko, arches, uuid, CardComponentViewModel, CardMultiSelectViewModel, WorkbenchComponentViewModel, fileRenderers, TileModel) {
   
    function viewModel(params) {
        params.configKeys = ['acceptedFiles', 'maxFilesize'];
        var self = this;
        const interpretationValueid = '2eef4771-830c-494d-9283-3348a383dfd6';
        const briefTextValueid = '72202a9f-1551-4cbc-9c7a-73c02321f3ea';
        const datasetInfo = params.datasetInfo;

        if (datasetInfo["select-dataset-files-step"]){
            var datasetIds = datasetInfo["select-dataset-files-step"].savedData()?.parts.reduce(
                (acc, part) => {
                    if (part.datasetId) { 
                        acc.push(part.datasetId)
                    }
                    return acc;
                }, 
                []
            )
        } else if (datasetInfo["select-dataset-instances"]){
            var datasetIds = datasetInfo["select-dataset-instances"].savedData()?.digitalResources?.reduce(
                (acc, res) => {
                    if (res.resourceid && res.selected === true) { 
                        acc.push(res.resourceid)
                    }
                    return acc;
                }, 
                []
            )
        } else if (params.datasetInfoFromUploadFilesStep){
            var datasetIds = [params.datasetInfoFromUploadFilesStep['upload-files-step'].savedData().datasetId]
        }

        this.fileFormatRenderers = fileRenderers;
        this.fileStatementParameter = ko.observable();
        this.fileStatementInterpretation = ko.observable();
        this.selected = ko.observable();
        params.value({});
        this.dirty = ko.computed(function(){
            for (var value of Object.values(params.value())) {
                if(value.fileStatementParameter.dirty() || value.fileStatementInterpretation.dirty()){
                    return true;
                }
            }
            return false;
        });
        this.save = function(){
            for (var value of Object.values(params.value())) {
                if(value.fileStatementParameter.dirty()){
                    value.fileStatementParameter.save();
                }
                if(value.fileStatementInterpretation.dirty()){
                    value.fileStatementInterpretation.save();
                }
            }
            params.form.complete(true);
        };

        params.form.reset = function(){
            for (var value of Object.values(params.value())) {
                value.fileStatementParameter.reset();
                value.fileStatementInterpretation.reset();
            }
            var file = params.value()[self.selectedFile()['@tile_id']];
            self.fileStatementParameter(file.fileStatementParameter.fileStatement());
            self.fileStatementInterpretation(file.fileStatementInterpretation.fileStatement());
        };
        this.reset = params.form.reset;
        
        this.fileStatementParameter.subscribe(function(fp) {
            if(!!this.selectedFile()){
                var obj = params.value();
                var tileid = this.selectedFile()['@tile_id'];
                obj[tileid].fileStatementParameter.updateStatement(fp);
                params.value.valueHasMutated();
            }
        }, this);
        this.fileStatementInterpretation.subscribe(function(fp) {
            if(!!this.selectedFile()){
                var obj = params.value();
                var tileid = this.selectedFile()['@tile_id'];
                obj[tileid].fileStatementInterpretation.updateStatement(fp);
                params.value.valueHasMutated();
            }
        }, this);
        
        this.fileFormatRenderers.forEach(function(r){
            r.state = {};
            r.disabled = true;
        });

        var FileStatement = function(tileid, parenttileid, resourceInstanceId, fileStatement, statementTypeId){
            var self = this;
            if(!tileid){
                tileid = '';
            }
            var tileObj = {
                "tileid": tileid,
                "data": {
                    "ca227726-78ed-11ea-a33b-acde48001122": fileStatement,
                    "ca2272c6-78ed-11ea-a33b-acde48001122": [
                        statementTypeId
                    ],
                    "ca227582-78ed-11ea-a33b-acde48001122": [
                        "bc35776b-996f-4fc1-bd25-9f6432c1f349"
                    ]
                },
                "nodegroup_id": "ca226fe2-78ed-11ea-a33b-acde48001122",
                "parenttile_id": parenttileid,
                "resourceinstance_id": resourceInstanceId,
                "sortorder": 0,
                "tiles": {}
            };
            this.tile = new TileModel(tileObj);
            this.fileStatement = ko.observable(fileStatement);
            this._fs = ko.observable(fileStatement);
            this.updateStatement = function(newStatement){
                self.tile.get('data')['ca227726-78ed-11ea-a33b-acde48001122'] = newStatement;
                self.fileStatement(newStatement);
            };
            this.save = function(){
                self.tile.save(function(request, status, tileModel){
                    if(status === 'success'){
                        tileModel.set('tileid', request.responseJSON.tileid);
                        self._fs(self.fileStatement());
                    }
                });
            };
            this.dirty = ko.computed(function(){
                return this._fs() !== this.fileStatement();
            }, this);
            this.reset = function(){
                self.updateStatement(self._fs());
            };
        };

        this.digitalResources = ko.observableArray();
        this.getDigitalResource = function(resourceid) {
            window.fetch(arches.urls.api_resources(resourceid) + '?format=json&compact=false&v=beta')
                .then(function(response){
                    if(response.ok){
                        return response.json();
                    }
                })
                .then(function(data){
                    self.digitalResources.push(data);
                    var obj = params.value();
                    data.resource.File.forEach(function(datafile){
                        var fileTileid = datafile['@tile_id'];
                        if (!(fileTileid in obj)){
                            obj[fileTileid] = {
                                'fileStatementParameter': '',
                                'fileStatementInterpretation': ''
                            };
                        }

                        var getStatement = function(valueid){
                            var fileStatement;
                            try {
                                fileStatement = datafile.FIle_Statement.find(function(statement){
                                    return statement.FIle_Statement_type['concept_details'][0].valueid === valueid;
                                });
                            } catch(err) {}

                            if(fileStatement){
                                return new FileStatement(
                                    fileStatement['@tile_id'], fileTileid, resourceid, fileStatement.FIle_Statement_content['@display_value'], valueid
                                );
                            } else {
                                return new FileStatement(
                                    '', fileTileid, resourceid, '', valueid
                                );          
                            }
                        };

                        obj[fileTileid].fileStatementParameter = getStatement(briefTextValueid);
                        obj[fileTileid].fileStatementInterpretation = getStatement(interpretationValueid);
                        params.value(obj);    
                    });
                    if(self.digitalResources().length === 1){
                        self.selectedDigitalResource(self.digitalResources()[0]);
                        self.selectedFile(self.files()[0]);
                    }
                });
        };
        datasetIds.forEach(function(datasetId){
            self.getDigitalResource(datasetId);
        })

        this.digitalResourceFilter = ko.observable('');
        this.selectedDigitalResource = ko.observable();
        this.selectedDigitalResource.subscribe(function(selectedDigitalResource){
            this.files(selectedDigitalResource.resource.File);
            this.selectedFile(this.files()[0]);
        }, this);
        this.filteredDigitalResources = ko.pureComputed(function(){
            return this.digitalResources().filter(function(dr){
                return dr.resource.Name.Name_content['@display_value'].toLowerCase().includes(this.digitalResourceFilter().toLowerCase());
            }, this);
        }, this);

        this.displayContent = undefined;
        this.files = ko.observableArray();
        this.fileFilter = ko.observable('');
        this.selectedRenderer = ko.observable();
        this.selectedFile = ko.observable();
        // this.selectFile = function(selectedFile){
        // };
        this.selectedFile.subscribe(function(selectedFile){
            if(!!selectedFile){
                self.selected(true);
                self.displayContent = self.getDisplayContent(selectedFile.file_details[0]);
                const renderer = self.getFileFormatRenderer(selectedFile.file_details[0].renderer);
                require([renderer.component], () => {
                    self.selectedRenderer(renderer);
                });
                // self.selectedFile(selectedFile);
                var file = params.value()[selectedFile['@tile_id']];
                self.fileStatementParameter(file.fileStatementParameter.fileStatement());
                self.fileStatementInterpretation(file.fileStatementInterpretation.fileStatement());
            } else {
                // self.selectedFile.selected(false);
                self.fileStatementParameter(undefined);
                self.fileStatementInterpretation(undefined);
            }
        });
        this.filteredFiles = ko.pureComputed(function(){
            return this.files().filter(function(file){
                return file.file_details[0].name.toLowerCase().includes(this.fileFilter().toLowerCase());
            }, this);
        }, this);
        this.fileInterpretationTiles = ko.observableArray();

        this.getDisplayContent = function(tiledata){
            var iconclass;
            var availableRenderers;
            var url = ko.unwrap(tiledata.url) || ko.unwrap(tiledata.content);
            var type = ko.unwrap(tiledata.type);
            var name = ko.unwrap(tiledata.name);
            var rendererid = ko.unwrap(tiledata.renderer);
            var renderer = self.fileFormatRenderers.find(function(item) {
                return item.id === rendererid;
            });
            if (!renderer) {
                availableRenderers = self.getDefaultRenderers(type, tiledata);
                if (!renderer) {
                    availableRenderers = self.getDefaultRenderers(type, ko.unwrap(tiledata.name));
                }
            }
            if (renderer) {
                iconclass = renderer.iconclass;
            }
            var ret = {
                validRenderer: ko.observable(true),
                url: url, type: type, name: name, renderer: renderer, iconclass: iconclass, renderers: availableRenderers
            };
            ret.availableRenderers = self.getDefaultRenderers(type, ret);

            return ret;
        };


        this.applyToAll = ko.observable(false);

        // CardComponentViewModel.apply(this, [params]);

        // if (!this.card.staging) {
        //     CardMultiSelectViewModel.apply(this, [params]);
        // } else {
        //     this.card.staging.valueHasMutated();
        // }
        
        // if ('filter' in this.card === false) {
        //     this.card.filter = ko.observable('');
        // }
        // if ('renderer' in this.card === false) {
        //     this.card.renderer = ko.observable();
        // }

        this.fileRenderer = ko.observable();
        this.managerRenderer = ko.observable();

        // var getfileListNode = function(){
        //     var fileListNodeId;
        //     var fileListNodes = params.card.model.nodes().filter(
        //         function(val){
        //             if (val.datatype() === 'file-list' && self.card.nodegroupid == val.nodeGroupId())
        //                 return val;
        //         });
        //     if (fileListNodes.length) {
        //         fileListNodeId = fileListNodes[0].nodeid;
        //     }
        //     return fileListNodeId;
        // };

        // this.fileListNodeId = getfileListNode();
        this.acceptedFiles = ko.observable(null);

        // this.displayWidgetIndex = self.card.widgets().indexOf(self.card.widgets().find(function(widget) {
        //     return widget.datatype.datatype === 'file-list';
        // }));

        WorkbenchComponentViewModel.apply(this, [params]);
        this.workbenchWrapperClass = ko.observable('autoheight');

        // if (this.card && this.card.activeTab) {
        //     self.activeTab(this.card.activeTab);
        // } else {
        // }

        // this.activeTab.subscribe(function(val){
        //     self.card.activeTab = val;
        // });

        this.fileRenderer.subscribe(function(){
            if (['add', 'edit', 'manage'].indexOf(self.activeTab()) < 0) {
                self.activeTab(undefined);
            }
        });

        // self.card.tiles.subscribe(function(val){
        //     if (val.length === 0) {
        //         self.activeTab(null);
        //     }
        // });

        this.getFileFormatRenderer = function(rendererid) {
            return self.fileFormatRenderers.find(function(item) {
                return item.id === rendererid;
            });
        };
        
        // if (!this.card.checkrenderers) {
        //     this.card.checkrenderers = this.card.staging.subscribe(function(){
        //         var compatible = [];
        //         var compatibleIds = [];
        //         var allCompatible = true;
        //         var staging = self.card ? self.card.staging() : [];
        //         var staged = self.card.tiles().filter(function(tile){
        //             return staging.indexOf(tile.tileid) >= 0;  
        //         });
        //         staged.forEach(function(tile){
        //             var file = tile.data[self.fileListNodeId]()[0];
        //             var defaultRenderers = self.getDefaultRenderers(ko.unwrap(file.type), ko.unwrap(file.name));
        //             if (compatible.length === 0) {
        //                 compatible = defaultRenderers;
        //                 compatibleIds = compatible.map(function(x){return x.id;});
        //             } else {
        //                 allCompatible = defaultRenderers.every(function(renderer){
        //                     return compatibleIds.indexOf(renderer.id) > -1;
        //                 }); 
        //             }
        //         });
        //         self.fileFormatRenderers.forEach(function(r){
        //             if (compatibleIds.indexOf(r.id) === -1 || allCompatible === false) {
        //                 r.disabled = true;
        //             } else {
        //                 r.disabled = false;
        //             }
        //         });
        //     });
        // }

        this.getDefaultRenderers = function(type, file){
            var defaultRenderers = [];
            this.fileFormatRenderers.forEach(function(renderer){
                var excludeExtensions = renderer.exclude ? renderer.exclude.split(",") : [];
                var rawFileType = type;
                var rawExtension = file.name ? ko.unwrap(file.name).split('.').pop() : ko.unwrap(file).split('.').pop();
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
                    url = ko.unwrap(tiledata.url) || ko.unwrap(tiledata.content);
                    type = ko.unwrap(tiledata.type);
                    name = ko.unwrap(tiledata.name);
                    rendererid = ko.unwrap(tiledata.renderer);
                    renderer = self.fileFormatRenderers.find(function(item) {
                        return item.id === rendererid;
                    });
                    if (!renderer) {
                        availableRenderers = self.getDefaultRenderers(type, tiledata);
                        if (!renderer) {
                            availableRenderers = self.getDefaultRenderers(type, ko.unwrap(tiledata.name));
                        }
                    }
                    if (renderer) {
                        iconclass = renderer.iconclass;
                    }
                }
            }
            file.availableRenderers = self.getDefaultRenderers(type, this);
            file.validRenderer = ko.observable(true);
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
        // this.uniqueidClass = ko.computed(function() {
        //     return "unique_id_" + self.uniqueId;
        // });

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

        // this.displayContent = ko.computed(function(){
        //     var file;
        //     // var selected = this.card.tiles().find(
        //     //     function(tile){
        //     //         return tile.selected() === true;
        //     //     });
        //     // if (selected) {
        //     //     if (!this.selected() || (this.selected() && this.selected().tileid !== selected.tileid)) {
        //     //         this.selected(selected);
        //     //     }
        //     //     file = this.getUrl(selected);
        //     //     this.fileRenderer(file.renderer ? file.renderer.id : undefined);
        //     // }
        //     // else {
        //     //     this.selected(undefined);
        //     //     if (['add', 'edit', 'manage'].indexOf(self.activeTab()) < 0) {
        //     //         self.activeTab(undefined);
        //     //     }
        //     // }
        //     // if (file) {
        //     //     file.availableRenderers = self.getDefaultRenderers(file.type, file);
        //     //     file.validRenderer = ko.observable(true);
        //     // }
        //     // return file;
        // }, this).extend({deferred: true});

        // if (this.displayContent() === undefined) {
        //     this.activeTab(undefined);
        // }

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

        // this.stageFiltered = function() {
        //     self.card.staging([]);
        //     this.filteredTiles().forEach(function(tile){
        //         if (self.card.staging().indexOf(tile.tileid) < 0) {
        //             self.card.staging.push(tile.tileid);
        //         }
        //     });
        // };

        this.clearStaging = function() {
            self.card.staging([]);
        };

        // if (this.form && ko.unwrap(this.form.resourceId)) {
        //     this.card.resourceinstanceid = ko.unwrap(this.form.resourceId);
        // } else if (this.card.resourceinstanceid === undefined && this.card.tiles().length === 0) {
        //     this.card.resourceinstanceid = uuid.generate();
        // }

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
            // self.card.widgets().forEach(function(w) {
            //     if (w.node_id() === self.fileListNodeId) {
            //         if (ko.unwrap(w.attributes.config.acceptedFiles)) {
            //             self.acceptedFiles(ko.unwrap(w.attributes.config.acceptedFiles));
            //         }
            //     }
            // });
        };
        this.getAcceptedFiles();

        // this.dropzoneOptions = {
        //     url: "arches.urls.root",
        //     dictDefaultMessage: '',
        //     autoProcessQueue: false,
        //     uploadMultiple: true,
        //     autoQueue: false,
        //     acceptedFiles: self.acceptedFiles(),
        //     clickable: ".fileinput-button." + this.uniqueidClass(),
        //     previewsContainer: '#hidden-dz-previews',
        //     init: function() {
        //         self.dropzone = this;
        //         this.on("addedfiles", function() {
        //             self.card.staging([]);
        //         });
        //         this.on("addedfile", self.addTile, self);
        //         this.on("error", function(file, error) {
        //             file.error = error;
        //         });
        //     }
        // };
    }

    ko.components.register('file-interpretation-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/upload-dataset/file-interpretation-step.htm'
        }
    });

    return viewModel;
});