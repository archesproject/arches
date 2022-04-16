define(['arches', 'models/abstract', 'utils/set-csrf-token'], function(arches, AbstractModel) {
    return AbstractModel.extend({
        url: arches.urls.tile,

        defaults: {
            'tileid': '',
            'data': '',
            'nodegroup_id': '',
            'parenttile_id': '',
            'resourceinstance_id': ''
        },

        save: function(callback, scope, fd) {
            fd || (fd = new FormData());
            delete fd.data;
            fd.append('data', JSON.stringify(this.toJSON()));
            var method = "POST";
            return this._doRequest({
                type: method,
                processData: false,
                contentType: false,
                url: this._getURL(method),
                data: fd
            }, callback, scope, 'save');
        }
    });
});
