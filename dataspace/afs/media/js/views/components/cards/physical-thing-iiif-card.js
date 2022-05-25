define([
    'knockout',
    'underscore',
    'views/components/cards/iiif-card',
    'utils/physical-thing'
], function(ko, _, IIIFCardComponentViewModel, physicalThingUtils) {
    return ko.components.register('physical-thing-iiif-card', {
        viewModel: function(params) {
            var self = this;
            IIIFCardComponentViewModel.apply(this, [params]);
            if (this.form && this.state === 'form') {
                var tiles = [];
                ko.unwrap(this.form.topCards).reduce(function(tiles, card) {
                    ko.unwrap(card.tiles).forEach(function(tile) {
                        tiles.push(tile);
                        tiles.concat(self.getTiles(tile));
                    });
                    return tiles;
                }, tiles);
                tiles = tiles.map(function(tile) {
                    return tile.getData();
                });
                this.loading(true);
                physicalThingUtils.getManifests(tiles).then(function(manifests) {
                    self.loading(false);
                    if (manifests.length > 0) {
                        self.manifest(manifests[0]);
                        self.getManifestData();
                    }
                });
            }
        },
        template: { require: 'text!templates/views/components/cards/iiif-card.htm' }
    });
});