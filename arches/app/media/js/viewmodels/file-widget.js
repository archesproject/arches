import ko from 'knockout';
import _ from 'underscore';
import $ from 'jquery';
import arches from 'arches';
import Dropzone from 'dropzone';
import uuid from 'uuid';
import WidgetViewModel from 'viewmodels/widget';
import 'bindings/dropzone';


/**
 * A viewmodel used for file widgets
 *
 * @constructor
 * @name FileWidgetViewModel
 *
 * @param  {string} params - a configuration object
 */
var FileWidgetViewModel = function(params) {
    var self = this;
    params.configKeys = ['acceptedFiles', 'maxFilesize', 'maxFiles'];

    WidgetViewModel.apply(this, [params]);

    this.uploadMulti = ko.observable(true);
    this.filesForUpload = ko.observableArray();
    this.uploadedFiles = ko.observableArray();
    this.unsupportedImageTypes = ['tif', 'tiff', 'vnd.adobe.photoshop'];


    if (this.form) {
        this.form.on('after-update', function(req, tile) {
            var hasdata = _.filter(tile.data, function(val, key) {
                val = ko.unwrap(val);
                if (val) {
                    return val;
                }
            });
            if (tile.isParent === true || hasdata.length === 0){
                if (self.dropzone) {
                    self.dropzone.removeAllFiles(true);
                }
            } else if ((self.tile === tile || _.contains(tile.tiles, self.tile)) && req.status === 200) {
                if (self.filesForUpload().length > 0) {
                    self.filesForUpload.removeAll();
                }
                var data = req.responseJSON.data[self.node.nodeid];
                if (Array.isArray(data)) {
                    self.uploadedFiles(data);
                }
                if (self.dropzone) {
                    self.dropzone.removeAllFiles(true);
                }
                self.formData.delete('file-list_' + self.node.nodeid);
            }
        });
        this.form.on('tile-reset', function(tile) {
            if ((self.tile === tile || _.contains(tile.tiles, self.tile))) {
                if (self.filesForUpload().length > 0) {
                    self.filesForUpload.removeAll();
                }
                if (Array.isArray(self.value())) {
                    var uploaded = _.filter(self.value(), function(val) {
                        return ko.unwrap(val.status) === 'uploaded';
                    });
                    self.uploadedFiles(uploaded);
                }
                if (self.dropzone) {
                    self.dropzone.removeAllFiles(true);
                    self.formData.delete('file-list_' + self.node.nodeid);
                }
            }
            self.beforeChangeMetadataSnapshot({});
        });
    }
    this.acceptedFiles.subscribe(function(val) {
        if (self.dropzone) {
            self.dropzone.hiddenFileInput.setAttribute("accept", val);
        }
    });
    this.maxFilesize.subscribe(function(val) {
        if (self.dropzone) {
            self.dropzone.options.maxFilesize = val;
        }
    });

    this.formatSize = function(file) {
        var bytes = ko.unwrap(file.size);
        if(bytes == 0) return '0 Byte';
        var k = 1024;
        var dm = 2;
        var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        return '<span>' + parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + '</span> ' + sizes[i];
    };

    this.createStrObject = str => {
        return {[arches.activeLanguage]: {
            "direction": arches.languages.find(lang => lang.code == arches.activeLanguage).default_direction,
            "value": str,
        }};
    };
    this.activeLanguage = arches.activeLanguage;

    this.beforeChangeMetadataSnapshot = ko.observable({});
    this.standaloneObservable = ko.observableArray();

    this.filesJSON = ko.computed(function() {
        var filesForUpload = self.filesForUpload();
        const uploadedFiles = self.uploadedFiles().map(file => {
            if (ko.isObservable(file.title[self.activeLanguage].value)) {
                return file;
            }
            // Rewrap in observable if needed.
            return {
                ...file,
                altText: {
                    ...file.altText,
                    [self.activeLanguage]: {
                        "direction": ko.observable(file.altText[self.activeLanguage].direction),
                        "value": ko.observable(file.altText[self.activeLanguage].value),
                    },
                },
                title: {
                    ...file.title,
                    [self.activeLanguage]: {
                        "direction": ko.observable(file.title[self.activeLanguage].direction),
                        "value": ko.observable(file.title[self.activeLanguage].value),
                    },
                },
                attribution: {
                    ...file.attribution,
                    [self.activeLanguage]: {
                        "direction": ko.observable(file.attribution[self.activeLanguage].direction),
                        "value": ko.observable(file.attribution[self.activeLanguage].value),
                    },
                },
                description: {
                    ...file.description,
                    [self.activeLanguage]: {
                        "direction": ko.observable(file.description[self.activeLanguage].direction),
                        "value": ko.observable(file.description[self.activeLanguage].value),
                    },
                },
            };
        });

        var standaloneObservable = self.standaloneObservable();  // for triggering update
        var beforeChangeMetadataSnapshot = self.beforeChangeMetadataSnapshot();
        return uploadedFiles.concat(
            _.map(filesForUpload, function(file, i) {
                return {
                    name: file.name,
                    altText: beforeChangeMetadataSnapshot[i]?.altText ?? self.createStrObject(''),
                    title: beforeChangeMetadataSnapshot[i]?.title ?? self.createStrObject(''),
                    attribution: beforeChangeMetadataSnapshot[i]?.attribution ?? self.createStrObject(''),
                    description: beforeChangeMetadataSnapshot[i]?.description ?? self.createStrObject(''),
                    accepted: file.accepted,
                    height: file.height,
                    lastModified: file.lastModified,
                    size: file.size,
                    status: file.status,
                    type: file.type,
                    width: file.width,
                    url: null,
                    file_id: null,
                    index: i,
                    content: URL.createObjectURL(file),
                    error: file.error
                };
            })
        );
    }).extend({throttle: 100});

    this.filesJSON.subscribe(function(value) {
        if (self.formData) {
            if (_.contains(self.formData.keys(), 'file-list_' + self.node.nodeid)) {
                self.formData.delete('file-list_' + self.node.nodeid);
            }
        }
        if (value.length > 1 && self.selectedFile() == undefined) { self.selectedFile(value[0]); }
        _.each(self.filesForUpload(), function(file) {
            if (file.accepted) {
                self.formData.append('file-list_' + self.node.nodeid, file, file.name);
            }
        });
        if (ko.unwrap(self.value) !== null || self.filesForUpload().length !== 0 || self.uploadedFiles().length !== 0) {
            self.value(
                value.filter(function(file) {
                    return file.accepted;
                })
            );
        }
    });

    this.equalMetadata = (a, b) => {
        if (!a || !b) {
            return false;
        }
        return (
            a.altText[this.activeLanguage].value === b.altText[this.activeLanguage].value
            && a.title[this.activeLanguage].value === b.title[this.activeLanguage].value
            && a.attribution[this.activeLanguage].value === b.title[this.activeLanguage].value
            && a.description[this.activeLanguage].value === b.title[this.activeLanguage].value
        );
    };

    this.metadataIsEmpty = (metadata) => {
        return !metadata.altText[this.activeLanguage].value
            && !metadata.title[this.activeLanguage].value
            && !metadata.attribution[this.activeLanguage].value
            && !metadata.description[this.activeLanguage].value
    };

    this.filesJSON.subscribe(function(value) {
        // Preserve current metadata for yet-to-be-uploaded files
        value.filter(
            file => file.file_id === null
            // Don't take a snapshot of the unsaved metadata if we're deleting it.
            && self.filesForUpload().find(f => f.name === file.name)
        ).forEach((file, i) => {
            const { altText, title, attribution, description } = file;
            const metadata = { altText, title, attribution, description };
            if (self.metadataIsEmpty(metadata)) {
                return;
            }
            if (!self.equalMetadata(self.beforeChangeMetadataSnapshot()[i], metadata)) {
                self.beforeChangeMetadataSnapshot()[i] = metadata;
                self.standaloneObservable.push(Math.random());
            }
        });
    }, this, 'beforeChange');

    this.getFileUrl = function(urltoclean) {
        const url = ko.unwrap(urltoclean);
        const httpRegex = /^https?:\/\//;
        // test whether the url is fully qualified or already starts with url_subpath
        return !url || httpRegex.test(url) || url.startsWith(arches.urls.url_subpath) ? url :
            (arches.urls.url_subpath + url).replace('//', '/');
    };

    if (Array.isArray(self.value())) {
        // Hydrate the metadata fields in place with the active language keys if missing
        const vals = self.value();
        vals.forEach(val => {
            ['altText', 'title', 'attribution', 'description'].forEach(metadataAttr => {
                if (!val[metadataAttr]) {
                    // Metadata fields missing entirely
                    val[metadataAttr] = self.createStrObject('');  // ensures active language
                } else if (!val[metadataAttr][arches.activeLanguage]) {
                    // Active language missing
                    val[metadataAttr][arches.activeLanguage] = self.createStrObject('')[arches.activeLanguage];
                }
            });
        });
        this.uploadedFiles(vals);
    }
    this.filter = ko.observable("");
    this.filteredList = ko.computed(function() {
        var arr = [], lowerName = "", filter = self.filter().toLowerCase();
        if(filter) {
            self.filesJSON().forEach(function(f, i) {
                lowerName = ko.unwrap(f.name).toLowerCase();
                if(lowerName.includes(filter)) { arr.push(self.filesJSON()[i]); }
            });
        }
        return arr;
    });

    this.selectedFile = ko.observable(self.filesJSON()[0]);
    this.selectFile = function(sFile) { self.selectedFile(sFile); };

    this.removeFile = function(file) {
        var filePosition;
        self.filesJSON().forEach(function(f, i) { if (f.file_id === file.file_id) { filePosition = i; } });
        self.shiftMetadata(filePosition);
        var newfilePosition = filePosition === 0 ? 1 : filePosition - 1;
        var filesForUpload = self.filesForUpload();
        var uploadedFiles = self.uploadedFiles();
        if (file.file_id) {
            file = _.find(uploadedFiles, function(uploadedFile) {
                return ko.unwrap(file.file_id) === ko.unwrap(uploadedFile.file_id);
            });
            self.uploadedFiles.remove(file);
        } else {
            file = filesForUpload[file.index];
            self.filesForUpload.remove(file);
        }
        if (self.filesJSON().length > 0) { self.selectedFile(self.filesJSON()[newfilePosition]); }
    };

    this.pageCt = ko.observable(5);
    this.pageCtReached = ko.computed(function() {
        return (self.filesJSON().length > self.pageCt() ? 'visible' : 'hidden');
    });

    this.pagedList = function(list) {
        var arr = [], i = 0;
        if(list.length > self.pageCt()) {
            while(arr.length < self.pageCt()) { arr.push(list[i++]); }
            return arr;
        }
        return list;
    };

    this.unique_id = uuid.generate();
    this.uniqueidClass = ko.computed(function() {
        return "unique_id_" + self.unique_id;
    });

    this.metadataDrawerCollapsedStatus = ko.observable({});  // 0-indexed. true = collapsed
    this.toggleDropdown = (index) => {
        const drawer = $(`.file-metadata-additional-${self.unique_id}${index}`)[0];
        if (!drawer) {
            self.metadataDrawerCollapsedStatus({
                ...self.metadataDrawerCollapsedStatus(),
                [index]: true,
            });
            return;
        }

        self.metadataDrawerCollapsedStatus({
            ...self.metadataDrawerCollapsedStatus(),
            [index]: drawer.className.includes('collapse in'),
        });
    };

    self.shiftMetadata = function(filePosition) {
        const newToggles = {};
        var someDrawerWasOpenAfterRemovedPosition = false;
        for (const [key, val] of Object.entries(self.metadataDrawerCollapsedStatus())) {
            const keyAsInt = Number.parseInt(key);
            if (keyAsInt < filePosition) {
                newToggles[keyAsInt] = val;
            } else if (keyAsInt !== filePosition && !someDrawerWasOpenAfterRemovedPosition) {
                newToggles[keyAsInt - 1] = val;
                if (val) {
                    // Only the first of these seems to work (bootstrap bug?)
                    // So set a flag to ensure we close subsequent drawers.
                    someDrawerWasOpenAfterRemovedPosition = true;
                }
            }
        }
        self.metadataDrawerCollapsedStatus(newToggles);

        const newMetadata = {};
        for (const [key, val] of Object.entries(self.beforeChangeMetadataSnapshot())) {
            const keyAsInt = Number.parseInt(key);
            if (keyAsInt < filePosition) {
                newMetadata[keyAsInt] = val;
            } else if (keyAsInt !== filePosition) {
                newMetadata[keyAsInt - 1] = val;
            }
        }
        self.beforeChangeMetadataSnapshot(newMetadata);
    }

    this.dropzoneOptions = {
        url: "arches.urls.root",
        dictDefaultMessage: '',
        autoProcessQueue: false,
        previewTemplate: $("template#file-widget-dz-preview").html(),
        autoQueue: false,
        previewsContainer: ".dz-previews." + this.uniqueidClass(),
        clickable: ".fileinput-button." + this.uniqueidClass(),
        acceptedFiles: this.acceptedFiles(),
        maxFilesize: this.maxFilesize(),
        uploadMultiple: self.uploadMulti(),
        // maxFiles: Number(this.maxFiles()),
        init: function() {
            self.dropzone = this;

            this.on("addedfile", function(file) {
                self.filesForUpload.push(file);
            });

            this.on("error", function(file, error) {
                file.error = error;
                self.filesForUpload.valueHasMutated();
            });

            this.on("removedfile", function(file) {
                self.filesForUpload.remove(file);
            });
        }
    };

    this.reset = function() {
        if (self.dropzone) {
            self.dropzone.removeAllFiles(true);
            self.uploadedFiles.removeAll();
            self.filesForUpload.removeAll();
            self.beforeChangeMetadataSnapshot({});
        }
    };

    this.displayValue = ko.computed(function() {
        return self.uploadedFiles().length === 1 ? ko.unwrap(self.uploadedFiles()[0].name) : self.uploadedFiles().length;
    });

    this.reportFiles = ko.computed(function() {
        return self.uploadedFiles().filter(function(file) {
            var fileType = ko.unwrap(file.type);
            if (fileType) {
                var ext = fileType.split('/').pop();
                return fileType.indexOf('image') < 0 || self.unsupportedImageTypes.indexOf(ext) > -1;
            }
            return true;
        });
    });

    this.reportImages = ko.computed(function() {
        return self.uploadedFiles().filter(function(file) {
            var fileType = ko.unwrap(file.type);
            if (fileType) {
                var ext = fileType.split('/').pop();
                return fileType.indexOf('image') >= 0 && self.unsupportedImageTypes.indexOf(ext) <= 0;
            }
            return false;
        });
    });
};

export default FileWidgetViewModel;
