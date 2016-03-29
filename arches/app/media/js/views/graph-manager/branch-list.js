define([
    'views/list'
], function(ListView) {
    var BranchList = ListView.extend({
        initialize: function(options) {
            ListView.prototype.initialize.apply(this, arguments);
            this.items = options.branches;
        }
    });
    return BranchList;
});
