define(['jquery', 'backbone', 'knockout'], function ($, Backbone, ko) {
    return Backbone.View.extend({

        initialize: function(options) {
            $.extend(this, options);            

            this.query = {
                filter:  {
                    // terms: ko.observableArray()
                },
                changed: ko.pureComputed(function(){
                    //
                }, this)
            };         
        }
    });
});