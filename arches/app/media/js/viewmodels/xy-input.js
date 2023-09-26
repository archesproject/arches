define(['knockout', 'underscore', 'arches', 'proj4', 'turf'], function(ko, _, arches, proj4, turf) {
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
        this.projBounds = arches.hexBinBounds;
        this.defaultProjection = _.findWhere(arches.preferredCoordinateSystems, {default: true}).proj4;
        this.defaultProjection ? this.srid = ko.observable(this.defaultProjection) : this.srid('4326');
        this.defaultCoords = (this.srid() === '4326') ? [arches.mapDefaultX, arches.mapDefaultY] : proj4(this.srid(), [arches.mapDefaultX, arches.mapDefaultY]);
        this.x = ko.observable();
        this.y = ko.observable();
        this.validCoords = ko.observable(false);
        this.boundsWarning = ko.observable(false);
        this.selectedPoint = ko.observable();
        this.availableSrids = _.map(arches.preferredCoordinateSystems, function(v, k) {
            var id = (k === '4326') ? '4326' : v.proj4;
            return {id: id, text: v.name};
        });

        this.setMap = function(map) {
            self.map = map;
        };

        this.coordinates = ko.computed(function() {
            var srcProj = self.srid();
            var res = [undefined, undefined];
            (self.x() && self.y()) ? self.validCoords(true) : self.validCoords(false);
            if (self.validCoords()) {
                res = ( srcProj === '4326') ? [Number(self.x()), Number(self.y())] : proj4(srcProj).inverse([Number(self.x()), Number(self.y())]);
                self.boundsWarning((!turf.inside(turf.point(res), turf.bboxPolygon(self.projBounds)) && self.active() === true));
            }
            return res;
        });

        this.transformCoords = function(val){
            if (!(self.x() && self.y())) {
                self.x(self.defaultCoords[0]);
                self.y(self.defaultCoords[1]);
            }
            if (self.x() && self.y()) {
                var projectedVals;
                if (self.srid() === '4326') {
                    projectedVals = proj4(self.defaultProjection).inverse([Number(self.x()), Number(self.y())]);
                } else if (self.defaultProjection === '4326') {
                    projectedVals = proj4(self.srid(), [Number(self.x()), Number(self.y())]);
                } else {
                    projectedVals = proj4(self.defaultProjection, self.srid(), [Number(self.x()), Number(self.y())]);
                }
                self.x(projectedVals[0]);
                self.y(projectedVals[1]);
                self.defaultProjection = self.srid();
            }
        };

        this.srid.subscribe(this.transformCoords);

        this.clearCoordinates = function() {
            self.srid('4326');
            self.x(arches.mapDefaultX);
            self.y(arches.mapDefaultY);
            self.boundsWarning(false);
        };

        this.addLocation = function(){
            if (self.x() && self.y()) {
                var geom = {
                    "type": "Point",
                    "coordinates": _.map(self.coordinates(), function(coord){return ko.unwrap(coord);})
                };
                mapWidget.updateDrawLayerWithJson(JSON.stringify(geom));
            }
        };

        this.updateSelectedPoint = function(){
            var projected;
            if (mapWidget.draw.getSelected() && mapWidget.draw.getSelected().features) {
                const points = _.filter(mapWidget.draw.getSelected().features, function(item) {return _.some([item.geometry], {type:'Point'});});
                if (points.length > 0) {
                    self.selectedPoint(points[0]);
                    var x = points[0].geometry.coordinates[0];
                    var y = points[0].geometry.coordinates[1];
                    projected = self.srid() === '4326' ? [x, y] : proj4(self.srid(),[x, y]);
                    self.x(projected[0]), self.y(projected[1]);
                } else {
                    if (self.selectedPoint() && !_.contains(['draw_point','draw_polygon','draw_line_string'], mapWidget.draw.getMode())) {
                        self.active(false);
                        self.selectedPoint(undefined);
                    }
                }
            }
        };

        this.active.subscribe(function(val){
            var points = [];
            if (mapWidget.context === 'search-filter') {
                if (val) {
                    if (mapWidget.extentSearch()) {
                        mapWidget.toggleExtentSearch();
                    } else {
                        mapWidget.deactivateDrawTools();
                        mapWidget.draw.deleteAll();
                        mapWidget.value({
                            "type": "FeatureCollection",
                            "features": []
                        });
                    }
                }
            } else {
                self.updateSelectedPoint();
            }
        });

        this.transformCoords();
    };

    return XYInputViewModel;
});
