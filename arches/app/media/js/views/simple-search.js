import $ from 'jquery';
import Backbone from 'backbone';
import 'select-woo';

export default Backbone.View.extend({
    initialize: function() {
        this.$el.find('.arches_simple_search').select2({
            minimumResultsForSearch: 10
        });
    }
});
