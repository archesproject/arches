define(['knockout', 'proj4', 'arches'], function (ko, proj4, arches) {
    /**
    * A base viewmodel for maptools
    *
    * @constructor
    * @name XYInputViewModel
    *
    * @param  {string} params - a configuration object
    */
    var XYInputViewModel = function(params) {
        var self = this;
        var mapWidget = params.mapWidget;
        this.active = ko.observable(false);
        this.defaultProjection = _.findWhere(arches.preferredCoordinateSystems, {default: true}).proj4
        this.defaultProjection ? this.srid = ko.observable(this.defaultProjection) : this.srid('4326');
        this.defaultCoords = (this.srid() === '4326') ? [arches.mapDefaultX, arches.mapDefaultY] : proj4(this.srid(), [arches.mapDefaultX, arches.mapDefaultY]);
        this.x = ko.observable(this.defaultCoords[0]);
        this.y = ko.observable(this.defaultCoords[1]);
        this.availableSrids = _.map(arches.preferredCoordinateSystems, function(v, k) {
            var id = (k === '4326') ? '4326' : v.proj4;
            return {id: id, text: v.name}
        })

        this.setMap = function (map) {
                self.map = map;
            }

        this.coordinates = ko.computed(function() {
            var srcProj = self.srid();
            var res = ( srcProj === '4326') ? [Number(self.x()), Number(self.y())] : proj4(srcProj).inverse([self.x(), self.y()]);
            return res;
        })

        this.clearCoordinates = function() {
            self.x(null);
            self.y(null);
        }

        this.addLocation = function(){
            var geom = {
                    "type": "Point",
                    "coordinates": _.map(self.coordinates(), function(coord){return ko.unwrap(coord)})
                }
            mapWidget.updateDrawLayerWithJson(JSON.stringify(geom))
            }

        this.active.subscribe(function(val){
            if (mapWidget.context === 'search-filter') {
                if (val) {
                    if (mapWidget.extentSearch()) {
                        mapWidget.toggleExtentSearch()
                    } else {
                        mapWidget.deactivateDrawTools();
                        mapWidget.draw.deleteAll();
                        mapWidget.value({
                            "type": "FeatureCollection",
                            "features": []
                        });
                    };
                };
            }
        });
    };

    return XYInputViewModel;
});

//663952
//5899830
