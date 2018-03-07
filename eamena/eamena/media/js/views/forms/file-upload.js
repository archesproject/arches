define(['jquery', 
    'underscore', 
    'knockout',
    'knockout-mapping',
    'views/forms/wizard-base', 
    'views/forms/sections/branch-list',
    'arches',
    'dropzone',
    'blueimp-gallery',
    'blueimp-jquery',
    ], function ($, _, ko, koMapping, WizardBase, BranchList, arches, dropzone, Gallery) {

    return WizardBase.extend({
        initialize: function() {
            WizardBase.prototype.initialize.apply(this);

            var self = this;
            var filetoupload;
            var dropzoneEl = this.$el.find('.dropzone');

            // detect if dropzone is attached, and if not init
            if (!dropzoneEl.hasClass('dz-clickable')) {
                this.dropzoneInstance = new dropzone(dropzoneEl[0], {
                    url: arches.urls.dropzone_files,
                    acceptedFiles: 'image/*, application/pdf, text/*, .doc, .docx',
                    uploadMultiple: false,
                    addRemoveLinks: true,
                    autoProcessQueue: false,
                    ignoreHiddenFiles: true,
                    maxFiles: 1,
                    parallelUploads: 1
                });

                this.dropzoneInstance.on("addedfile", function(file) {
                    $('#cancel-workflow').removeClass('disabled');
                    $('#end-workflow').removeClass('disabled');      
                    if (this.files.length === 1){
                        var id = 0;//_.uniqueId('file_');
                        filetoupload = file;
                        filetoupload.id = id;
                        filetoupload.hiddenFileInput = self.el.appendChild(this.hiddenFileInput);
                        filetoupload.hiddenFileInput.setAttribute('name', id);
                        this.hiddenFileInput = false;
                    }else{
                        var modaldialog = $('#one_file_only_modal');
                        modaldialog.modal().show();
                        this.removeFile(file);
                    }
                });

                this.dropzoneInstance.on("removedfile", function(filetoremove) {
                    $('#cancel-workflow').addClass('disabled');
                    $('#end-workflow').addClass('disabled');   
                    if ('id' in filetoremove){
                        self.el.removeChild(filetoupload.hiddenFileInput);
                        filetoupload = undefined;
                    }
                });
                this.dropzoneInstance.on("sending", function(file, xhr, formData){
                    var formValues = $('#formdata').val();
                    formData.append('formdata', formValues);
                });
                this.dropzoneInstance.on('complete', function(){
                    location.reload();
                });
            }

            this.inforesourcebranch = this.addBranchList(new BranchList({
                el: this.$el.find('#file-section')[0],
                data: this.data,
                dataKey: 'INFORMATION_RESOURCE.E73',
                validate: function(){
                    return true;
                },
                confirmDelete: function(){
                    var modaldialog = $('#confirm_delete_modal');
                    modaldialog.modal().show();
                },
                deleteItem: function(branchlist, e) {
                    $('#confirm_delete_modal').hide();
                    this.removefilepathnode();
                    self.submit(e);
                    
                },
                removefilepathnode: function(){
                    var nodetoremove;
                    _.each(this.viewModel.branch_lists()[0].nodes(), function(node, i){
                        if (node.entitytypeid() === 'FILE_PATH.E62'){
                            nodetoremove = node;
                        }
                    }, this);
                    if (nodetoremove !== undefined){
                        this.viewModel.branch_lists()[0].nodes.remove(nodetoremove);
                    }
                    if (filetoupload !== undefined){
                        self.el.removeChild(filetoupload.hiddenFileInput);
                    }
                },
                                      
            }));
        },
        submit: function(evt){
            if (this.validate()){
                evt.preventDefault();
                evt.stopPropagation();
                if (this.dropzoneInstance.files.length !== 0) {
                    this.dropzoneInstance.processQueue();
                }else{
                    this.form.submit(); 
                }
            }
        }
    });
});