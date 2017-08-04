define(['knockout', 'knockout-mapping', 'proj4', 'arches'], function (ko, koMapping, proj4, arches) {
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
        var mapWidget = params.mapWidget
        this.active = ko.observable(false);
        this.srid = ko.observable('+proj=utm +zone=30 +datum=WGS84 +units=m +no_defs');
        this.x = ko.observable(622287.797002);
        this.y = ko.observable(5991003.038972);
        this.availableSrids = [{
                                text: 'Lat/Lon',
                                id: '4326'
                            }, {
                                text: 'UTM 30N',
                                id: '+proj=utm +zone=30 +datum=WGS84 +units=m +no_defs'
                            }]

        this.setMap = function (map) {
                self.map = map;
            }

        this.coordinates = ko.computed(function() {
            var res = [Number(self.x()), Number(self.y())]
            var srcProj = self.srid();
            if (srcProj !== '4326') {
                res = proj4(srcProj).inverse([self.x(), self.y()]);
            }
            return res
        })
        // for testing UTM 30N: 622287.797002, 5991003.038972 === 4326: -1.1319575769761, 54.052734375
        this.coordinates.subscribe(function(val){
            console.log(val);
        })

        this.addLocation = function(){
            var feature = {
              "type": "Feature",
              "properties": {},
              "geometry": {
                "type": "Point",
                "coordinates": self.coordinates
              }
            }

            var fc = {
              "type": "FeatureCollection",
              "features": [feature]
            }

            if (mapWidget.value()) {
                var currentValue = koMapping.toJS(mapWidget.value)
                currentValue.features.push(feature);
                mapWidget.value(currentValue);
            } else {
                mapWidget.value(fc)
            }
        }

    };

    return XYInputViewModel;
});
