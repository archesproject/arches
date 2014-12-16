define(['jquery', 'backbone', 'models/concept', 'models/value', 'select2'], function ($, Backbone, ConceptModel, ValueModel) {
    return Backbone.View.extend({
        initialize: function() {
            var data = [];
            var datanodes = this.$el.find('div[name="scheme_group_dd_data"] div').each(function(){
                data.push($(this).data());
            });
            
            this.scheme_group_dd = this.$el.find('[name="scheme_group_dd"]').select2({
                createSearchChoice:function(term, data) { 
                    if ( $(data).filter(function() { return this.text.localeCompare(term)===0; }).length===0) {
                        return {id:term, text:term};
                    } 
                },
                //minimumResultsForSearch: -1,
                data: data
            });
        },

        getSchemeGroupModelFromSelection: function(language){
            var conceptschemegroup = new ConceptModel({
                id: '',
                relationshiptype: 'narrower',
                nodetype: 'ConceptSchemeGroup'
            });

            var selection = this.scheme_group_dd.select2('data');
            if (selection.id == selection.text){
                // adding a new group
                var label = new ValueModel({
                    value: selection.text,
                    language: language,
                    category: 'label',
                    type: 'prefLabel'
                });
                conceptschemegroup.set('values', [label]);
                conceptschemegroup.set('legacyoid', selection.text);

            }else{
                // selecting an existing group
                conceptschemegroup.set('id', selection.id);
            }

            return conceptschemegroup;

        }
    });
});