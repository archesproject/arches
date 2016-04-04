define(['arches', 'models/abstract', 'underscore'], function (arches, AbstractModel, _) {
    return AbstractModel.extend({
        url: arches.urls.graph,

        defaults: {
            'nodes': [],
            'edges': [],
            'cards': []
        },

        appendBranch: function(nodeid, property, branchmetadatid, callback, scope){
            this._doRequest({
                type: "POST",
                url: this.url + 'append_branch/' + nodeid + '/' + property + '/' + branchmetadatid,
                data: JSON.stringify(this.toJSON())
            }, callback, scope, 'save');
        }


    });
});