define([
    'knockout',
    'knockout-mapping',
    'underscore',
    'arches',
    'dropzone',
    'uuid',
    'viewmodels/card-component',
    'views/components/workbench',
    'viewmodels/photo-gallery',
    'templates/views/components/cards/photo-gallery-card.htm',
    'viewmodels/alert',
    'bindings/slide',
    'bindings/fadeVisible',
    'bindings/dropzone',
    'bindings/gallery',
], function(ko, koMapping, _, arches, Dropzone, uuid, CardComponentViewModel, WorkbenchComponentViewModel, PhotoGallery, photoGalleryCardTemplate, AlertViewModel) {
    const viewModel = function(params) {

        params.configKeys = ['acceptedFiles', 'maxFilesize'];
        var self = this;
        CardComponentViewModel.apply(this, [params]);
        WorkbenchComponentViewModel.apply(this, [params]);
        if (this.card && this.card.activeTab) {
            self.activeTab(this.card.activeTab);
        }

        this.photoGallery = new PhotoGallery();
        this.lastSelected = 0;
        this.selected = ko.observable();
        self.activeTab.subscribe(function(val){self.card.activeTab = val;});
        self.card.tiles.subscribe(function(val){
            if (val.length === 0) {
                self.activeTab(null);
            }
        });

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

        this.maxFilesize = ko.computed(function(){
            var mfs = "Missing maxFilesize";
            self.card.widgets().forEach(function(widget){
                if (widget.node_id() === self.fileListNodeId) {
                    mfs = widget.config.maxFilesize() || "--";
                }
            });
            return mfs;
        });

        this.acceptedFiles = ko.computed(function(){
            return self.card.widgets().find(widget=>widget.node_id() === self.fileListNodeId)?.config.acceptedFiles() || arches.translations.allFormatsAccepted;
        });

        this.cleanUrl = function(url) {
            const httpRegex = /^https?:\/\//;
            return !url || httpRegex.test(url) || url.startsWith(arches.urls.url_subpath) ? url :
                (arches.urls.url_subpath + url).replace('//', '/');
        };

        this.getUrl = function(tile){
            var url = '';
            var name = '';
            var val = ko.unwrap(tile.data[this.fileListNodeId]);
            if (val && val.length == 1) {
                {
                    url = self.cleanUrl(ko.unwrap(val[0].url)) || ko.unwrap(val[0].content);
                    name = ko.unwrap(val[0].name);
                }
            }
            return {url: url, name: name};
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
                self.photoGallery.selectItem(self.card.tiles()[selectedIndex]);
            };
        };
        this.defaultSelector = this.selectDefault();

        this.displayContent = ko.pureComputed(function(){
            var photo;
            var selected = this.card.tiles().find(
                function(tile){
                    return tile.selected() === true;
                });
            if (selected) {
                this.selected(selected);
                photo = this.getUrl(selected).url;
            }
            else {
                this.selected(undefined);
            }
            return photo;
        }, this);

        if (this.displayContent() === undefined) {
            var selectedIndex = 0;
            if (
                this.card.tiles().length > 0 &&
                this.form &&
                (ko.unwrap(this.form.selection) && this.form.selection() !== 'root') ||
                (this.form && !ko.unwrap(this.form.selection))) {
                this.photoGallery.selectItem(this.card.tiles()[selectedIndex]);
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
            var acceptedFileFormats;
            var loadFile;
            acceptedFileFormats = ((ko.unwrap(self.acceptedFiles)).split(',').map(item=>item.trim())).map(format => format.replace('.', ''));
            if(ko.unwrap(self.acceptedFiles) != arches.translations.allFormatsAccepted && acceptedFileFormats !== undefined && acceptedFileFormats.length > 0){
                var fileType = file.name.split('.').pop().toLowerCase();
                if(acceptedFileFormats.includes(fileType)){
                    loadFile = true;
                }
                else{
                    loadFile = false;
                }
            }
            else{
                loadFile = true;
            }

            if (loadFile === true) {
                var newtile;
                newtile = self.card.getNewTile();
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
                    error: file.error
                };
                newtile.data[self.fileListNodeId]([tilevalue]);
                newtile.formData.append('file-list_' + self.fileListNodeId, file, file.name);
                newtile.resourceinstance_id = self.card.resourceinstanceid;
                if (self.card.tiles().length === 0) {
                    sleep(50);
                }
                newtile.save();
                self.card.newTile = undefined;
            }
            else{
                params.pageVm.alert(new AlertViewModel(
                    'ep-alert-red',
                    arches.translations.incorrectFileFormat,
                    arches.translations.fileFormatNotAccepted(ko.unwrap(self.acceptedFiles)),
                    null,
                    function(){}
                ));
            }
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
    };

    return ko.components.register('photo-gallery-card', {
        viewModel: viewModel,
        template: photoGalleryCardTemplate,
    });
});
