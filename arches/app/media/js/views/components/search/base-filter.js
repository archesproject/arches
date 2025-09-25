import $ from 'jquery';
import Backbone from 'backbone';
import ko from 'knockout';


export default Backbone.View.extend({
    constructor: function() {
        this.name = 'Base Filter';
        // the various filters managed by this widget
        this.filter = {};
        // Call the original constructor
        Backbone.View.apply(this, arguments);
    },

    initialize: function(options) {
        $.extend(this, options);
    },
});
