define(['jquery', 
    'underscore', 
    'knockout',
    'knockout-mapping',
    'views/forms/wizard-base', 
    'views/forms/sections/branch-list',
    'arches',
    'dropzone',
    'summernote',
    'blueimp-gallery',
    'blueimp-jquery',
    ], function ($, _, ko, koMapping, WizardBase, BranchList, arches, dropzone, summernote, Gallery) {
        


    return WizardBase.extend({

        initialize: function() {
            WizardBase.prototype.initialize.apply(this);

            var self = this;
            var dropzoneEl = this.$el.find('.dropzone'); 
            this.count = undefined;
            this.newfiles = ko.observableArray();  

            ko.applyBindings(this.newfiles, this.$el.find('#new-files-section')[0]);  

            // detect if dropzone is attached, and if not init
            if (!dropzoneEl.hasClass('dz-clickable')) {
                $('#cancel-workflow').removeClass('disabled');
                this.dropzoneInstance = new dropzone(dropzoneEl[0], {
                    url: arches.urls.dropzone_files,
                    acceptedFiles: 'image/*, application/pdf, text/*, .doc, .docx',
                    uploadMultiple: false,
                    addRemoveLinks: true,
                    autoProcessQueue: false,
                    ignoreHiddenFiles: true,
                    maxFiles: 10,
                    parallelUploads: 10
                });

                this.dropzoneInstance.on("addedfile", function(file) {
                    var el = self.el.appendChild(this.hiddenFileInput);
                    var id = file.name;
                    
                    $('#end-workflow').removeClass('disabled');      
                    if(self.count === undefined){
                        self.count = this.hiddenFileInput.files.length;
                    }
                    if (self.count === 1){
                        this.hiddenFileInput = false;
                        self.count = undefined;
                    }else{
                        self.count--
                    }

                    file.id = id;
                    el.setAttribute('name', id);
                    self.newfiles.push({
                        el: el,
                        id: id,
                        file: file,
                        title: ko.observable(file.name.split('.')[0]),
                        title_type: ko.observable(),
                        description: ko.observable(),
                        relationshiptype: ko.observable(),
                        thumbnail: ko.observable(),
                        domains: self.data['current-files'].domains
                    });
                });

                this.dropzoneInstance.on("removedfile", function(filetoremove) {
                    var index;
                    _.each(self.newfiles(), function(file, i){
                        if (file.id === filetoremove.id){
                            index = i;
                        }
                    }, this);

                    self.el.removeChild(self.newfiles()[index].el);
                    self.newfiles.splice(index, 1);
                    if(self.newfiles.count() === 0){
                        $('#cancel-workflow').addClass('disabled');
                        $('#end-workflow').addClass('disabled');                              
                    }
                    
                });

                this.dropzoneInstance.on("thumbnail", function(addedfile, thumbnaildata) {
                    _.each(self.newfiles(), function(file, i){
                        if (file.id === addedfile.id){
                            file.thumbnail(thumbnaildata);
                        }
                    }, this);
                });
                
                this.dropzoneInstance.on("sending", function(file, xhr, formData){
                    var formValues = $('#formdata').val();
                    formData.append('formdata', formValues);
                });
                this.dropzoneInstance.on('complete', function(){
                    location.reload();
                });
            }

            this.addBranchList(new BranchList({
                el: this.$el.find('#current-files-section')[0],
                data: this.data,
                dataKey: 'current-files',             
                validateBranch: function (nodes) {
                    return true;
                },
                editItem: function(branch){
                    var self = this;
                    BranchList.prototype.editItem.call(this, branch);
                    $('#title_box').show();
                    $('#title_h5').show();
                    $('#catalogue_box').show();
                    $('#catalogue_h5').show();                    
                    _.each(branch.nodes(), function(node){
                            if (node.entitytypeid() === 'TITLE.E41'){
                                $('#catalogue_box').hide();
                                $('#catalogue_h5').hide();
                            }else if (node.entitytypeid() === 'CATALOGUE_ID.E42') {
                                $('#title_box').hide();
                                $('#title_h5').hide();
                            }
                    }, this);
                    $('#deletewarning').slideUp();
                    $('#editform').slideDown();
                    $('#savebtn').show();
                    $('#deletebtn').hide();
                    
                    var modaldialog = $('#edit_file_resource_modal');
                    modaldialog.modal().show();              
                },
                updateItem: function(branchlist, evt){
                    var data = koMapping.toJS(this.getEditedBranch());
                    evt.preventDefault();
                    $('.form-load-mask').show();
                    self.form.find('#formdata').val(JSON.stringify({'current-files': data}));
                    self.form.submit();
                },
                confirmDelete: function(branchlist, evt){
                    $('#deletewarning').slideDown(500);
                    $('#editform').slideUp(500);
                    $('#savebtn').hide(500);
                    $('#deletebtn').show(500);
                },
                deleteItem: function(branchlist, evt){
                    var relationship = koMapping.toJS(branchlist.getEditedBranch().nodes.get('ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55'));
                    $.ajax({
                        url: arches.urls.related_resources + relationship.entityid1,
                        method: 'DELETE',
                        data: JSON.stringify(relationship),
                        success: function(response) {
                            branchlist.removeEditedBranch();
                        }
                    });
                },
                getData: function(){
                    return [];
                }
            }));

            this.newfilebranchlist = this.addBranchList(new BranchList({
                data: {'new-files':{'branch_lists': [], domains: this.data['current-files'].domains}},
                dataKey: 'new-files',
                validate: function(){
                    var valid = true;
                    _.each(self.newfiles(), function(item){
                        if (item.title() == undefined || item.title() == '' || item.relationshiptype() == undefined || item.relationshiptype() == ''){
                            valid = false;
                        }

                    }, this); 
                    return valid;
                },
                getData: function(){
                    var data = [];
                    _.each(self.newfiles(), function(item){
                        delete item.el;
                        delete item.file;
                        delete item.thumbnail;
                        delete item.domains;
                        data.push(item);
                        
                    }, this); 
                    return data
                }
            }));

        },
        submit: function(evt){
            var validationAlert = this.$el.find('.branch-invalid-alert');

            if (this.validate()){
                this.$el.find('.form-load-mask').show();
                this.form.find('#formdata').val(this.getData());
                evt.preventDefault();
                evt.stopPropagation();
                this.dropzoneInstance.processQueue();
                
            }else {
                validationAlert.show(300);
                setTimeout(function() {
                    validationAlert.fadeOut();
                }, 5000);
            }
        }        
    });
});