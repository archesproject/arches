define(['models/tile'], function (TileModel) {
    const arches = window.arches;

    return TileModel.extend({
        url: arches.urls.config
    });
});
