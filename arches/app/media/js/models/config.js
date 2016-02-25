define(['arches', 'models/tile'], function (arches, TileModel) {
    return TileModel.extend({
        url: arches.urls.config
    });
});
