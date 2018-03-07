 define(['jquery', 'underscore', 'knockout-mapping', 'views/forms/base', 'views/forms/sections/branch-list'], function ($, _, koMapping, BaseForm, BranchList) {
    return BaseForm.extend({
        initialize: function() {
            BaseForm.prototype.initialize.apply(this);
            var date_picker = $('.datetimepicker').datetimepicker({pickTime: false});
            date_picker.on('dp.change', function(evt){
                $(this).find('input').trigger('change');
            });            
            this.addBranchList(new BranchList({
                el: this.$el.find('#xref-section')[0],
                data: this.data,
                dataKey: 'URL.E51',
                validateBranch: function (nodes) {
                    return true;
                    return this.validateHasValues(nodes);
                }
            }));


//             this.addBranchList(new BranchList({
//                 el: this.$el.find('#xref-section')[0],
//                 data: this.data,
//                 dataKey: 'URL.E51',
//                 validateBranch: function(nodes){
//                     return this.validateHasValues(nodes);
//                 },
//                 isUrl: function(value) {
//                     return /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/.test(value);
//                 },
//                 getLink: function(value) {
//                     if (/^https?:\/\//.test(value)) {
//                         return value;
//                     } else {
//                         return 'http://' + value;
//                     }
//                 }
//             }));


        }
    });
});