define(['arches',
    'models/abstract',
    'knockout',
    'knockout-mapping',
    'underscore'
], function (arches, AbstractModel, ko, koMapping, _) {

    var FormModel = AbstractModel.extend({
        /**
        * A backbone model to manage form data
        * @augments AbstractModel
        * @constructor
        * @name FormModel
        */
        url: arches.urls.form,
        constructor: function(attributes, options){
            options || (options = {});
            options.parse = true;
            AbstractModel.prototype.constructor.call(this, attributes, options);
        },
        /**
         * parse - parses the passed in attributes into a {@link FormModel}
         * @memberof FormModel.prototype
         * @param  {object} attributes - the properties to seed a {@link FormModel} with
         */
        initialize: function(attributes) {
          this.formid = attributes.data.formid;
          this.iconclass = ko.observable(attributes.data.iconclass);
          this.title = ko.observable(attributes.data.title);
          this.subtitle = ko.observable(attributes.data.subtitle);
          this.status = ko.observable(attributes.data.status);
          this.visible = ko.observable(attributes.data.visible);
        },
        toJSON: function(){
            var ret = {};
            for(var key in this.attributes){
                console.log(key)
            }
            return ret;
        }
    });
    return FormModel;
});
