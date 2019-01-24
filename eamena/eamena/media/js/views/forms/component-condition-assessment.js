define(['jquery', 
    'underscore', 
    'knockout',
    'views/forms/wizard-base', 
    'views/forms/sections/branch-list',
    'views/forms/sections/validation',
    'bootstrap-datetimepicker',
    'summernote',
    'dropzone',
    'arches'], function ($, _, ko, WizardBase, BranchList, ValidationTools, datetimepicker, summernote, dropzone, arches) {
    var vt = new ValidationTools;
    return WizardBase.extend({
        initialize: function() {
            WizardBase.prototype.initialize.apply(this);

            var self = this;
            var date_picker = $('.datetimepicker').datetimepicker({pickTime: false});            
            this.getBlankFormData();
            date_picker.on('dp.change', function(evt){
                $(this).find('input').trigger('change'); 
            });
            self.startWorkflow();
            console.log('started workflow');
            console.log(this.branchLists);
            console.log(this.data);
            
            // step 1
            this.addBranchList(new BranchList({
                el: this.$el.find('#disturbances-section')[0],
                data: this.data,
                dataKey: 'DAMAGE_STATE.E3',
                validateBranch: function (nodes) {
                    var ck0 = vt.isValidDate(nodes,"DISTURBANCE_CAUSE_DATE_TO.E61");
                    var ck1 = vt.isValidDate(nodes,"DISTURBANCE_CAUSE_DATE_FROM.E61");
                    var ck2 = vt.isValidDate(nodes,"DISTURBANCE_CAUSE_DATE_OCCURRED_ON.E61");
                    var ck3 = vt.isValidDate(nodes,"DISTURBANCE_CAUSE_DATE_OCCURRED_BEFORE.E61");
                    var ck4 = vt.nodesHaveValues(nodes, {"mustBeFilled":["DISTURBANCE_CAUSE_CATEGORY_TYPE.E55"]});
                    return ck0 && ck1 && ck2 && ck3 && ck4
                }
            }));

            // step 2

            var dropzoneEl = this.$el.find('.dropzone');
            this.count = undefined;
            this.newfiles = ko.observableArray();

            ko.applyBindings(this.newfiles, this.$el.find('#new-image-section')[0]);

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
                    console.log("Sending dropzone", formValues);
                });
                this.dropzoneInstance.on('complete', function(){
                    location.reload();
                });
            }

            this.addBranchList(new BranchList({
                el: this.$el.find('#image-file-section')[0],
                data: this.data,
                dataKey: 'current-files',
                validateBranch: function (nodes) {
                    return true;
                }
            }));

            this.newfilebranchlist = this.addBranchList(new BranchList({
                data: {'new-files':{'branch_lists': [], domains: this.data['current-files'].domains}},
                dataKey: 'new-files',
                validate: function(){
                    console.log("IN file add BranchList!")
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

            this.addBranchList(new BranchList({
                el: this.$el.find('#image-title-section')[0],
                data: this.data,
                dataKey: 'CONDITION_ASSESSMENT_IMAGE_TITLE.E41',
                validateBranch: function(nodes) {
                    return this.validateHasValues(nodes)
                }
            }));
            this.addBranchList(new BranchList({
                el: this.$el.find('#image-caption-section')[0],
                data: this.data,
                dataKey: 'CONDITION_ASSESSMENT_IMAGE_DESCRIPTION.E62',
                validateBranch: function(nodes) {
                    return this.validateHasValues(nodes)
                }
            }));
            this.addBranchList(new BranchList({
                el: this.$el.find('#image-information-section')[0],
                data: this.data,
                dataKey: 'CONDITION_ASSESSMENT_IMAGE_CREATION.E65',
                validateBranch: function(nodes) {
                    return vt.mustHaveAtLeastOne(nodes)
                }
            }));
            
            // step 3
            this.addBranchList(new BranchList({
                el: this.$el.find('#potential-section')[0],
                data: this.data,
                dataKey: 'THREAT_INFERENCE_MAKING.I5',
                validateBranch: function (nodes) {
                   return vt.mustHaveAtLeastOne(nodes)
                }
            }));

            // step 4
            this.addBranchList(new BranchList({
                el: this.$el.find('#recommendation-section')[0],
                data: this.data,
                dataKey: 'ACTIVITY_PLAN.E100',
                validateBranch: function (nodes) {
                    return vt.mustHaveAtLeastOne(nodes)
                },
            }));
            this.addBranchList(new BranchList({
                el: this.$el.find('#priority-section')[0],
                data: this.data,
                dataKey: 'ACTIVITY_PLAN_PRIORITY_ASSIGNMENT.E13',
                validateBranch: function (nodes) {
                    return this.validateHasValues(nodes);
                },
            }));
            

            this.listenTo(this,'change', this.dateEdit)
            
            this.events['click .disturbance-date-item'] = 'showDate';
            this.events['click .disturbance-date-edit'] = 'dateEdit';
        },
        
        
        dateEdit: function (e, b) {
            _.each(b.nodes(), function (node) {
                if (node.entitytypeid() == 'DISTURBANCE_CAUSE_DATE_FROM.E61' && node.value() && node.value() != '') {
                    $('.div-date').addClass('hidden')
                    $('.div-date-from-to').removeClass('hidden')
                    $('.disturbance-date-value').html('From-To')
                } else if (node.entitytypeid() == 'DISTURBANCE_CAUSE_DATE_OCCURRED_ON.E61' && node.value() && node.value() != '') {
                    $('.div-date').addClass('hidden')
                    $('.div-date-on').removeClass('hidden')
                    $('.disturbance-date-value').html('On')
                } else if (node.entitytypeid() == 'DISTURBANCE_CAUSE_DATE_OCCURRED_BEFORE.E61' && node.value() && node.value() != '') {
                    $('.div-date').addClass('hidden')
                    $('.div-date-before').removeClass('hidden')
                    $('.disturbance-date-value').html('Before')
                }
            })
        },
        
        
        showDate: function (e) {
            $('.div-date').addClass('hidden')
            $('.disturbance-date-value').html($(e.target).html())
            if ($(e.target).hasClass("disturbance-date-from-to")) {
                $('.div-date-from-to').removeClass('hidden')
            } else if ($(e.target).hasClass("disturbance-date-on")) {
                $('.div-date-on').removeClass('hidden')
            } else if ($(e.target).hasClass("disturbance-date-before")) {
                $('.div-date-before').removeClass('hidden')
            }
        },

        startWorkflow: function() {
            
            this.switchBranchForEdit();
        },

        switchBranchForEdit: function(branchData){
            this.prepareData(branchData);

            _.each(this.branchLists, function(branchlist){
                branchlist.data = branchData;
                branchlist.undoAllEdits();
            }, this);

            this.toggleEditor();
        },

        prepareData: function(assessmentNode){
            _.each(assessmentNode, function(value, key, list){
                assessmentNode[key].domains = this.data.domains;
            }, this);
            return assessmentNode;
        },

        getBlankFormData: function(){
            return this.prepareData({
                
                // step 1
                'TEST': {
                    'branch_lists':[]
                },
                
                // step 2
                'CONDITION_ASSESSMENT_IMAGE.E38': {
                    'branch_lists':[]
                },
                
                // step 3
                'THREAT_INFERENCE_MAKING.I5': {
                    'branch_lists':[]
                },

                //step 4
                'ACTIVITY_PLAN.E100': {
                    'branch_lists':[]
                },
                'ACTIVITY_PLAN_PRIORITY_ASSIGNMENT.E13': {
                    'branch_lists':[]
                },
            })
        },
        cancelWorkflow: function() { 
            this.cancel(); 
        },
        submit: function(evt){
            evt.preventDefault();
            var validationAlert = this.$el.find('.wizard-invalid-alert');
            var hasnewdata = false;
            _.each(this.branchLists, function(branchList){
               if(branchList.dataKey === 'new-files' && branchList.getData().length > 0){
                   hasnewdata = true;
               }
            });

            if (this.validate()){
                this.$el.find('.form-load-mask').show();
                this.form.find('#formdata').val(this.getData());
                if(hasnewdata === true) {
                    evt.stopPropagation();
                    this.dropzoneInstance.processQueue();
                }else{
                    this.form.submit();
                }

            }else {
                validationAlert.show(300);
                setTimeout(function() {
                    validationAlert.fadeOut();
                }, 5000);
            }
        }

    });
});