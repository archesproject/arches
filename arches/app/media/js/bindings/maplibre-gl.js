import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import arches from 'arches';
import * as maplibre from 'maplibre-gl';

// maplibre-gl auto-detects its worker script via `import.meta.url`, which
// doesn't resolve correctly once bundled by webpack. Point it at the copy
// webpack emits as a static asset instead.
maplibre.setWorkerUrl(
    new URL('maplibre-gl/dist/maplibre-gl-worker.mjs', import.meta.url).href
);
// The worker script above imports this module by relative path at runtime.
// webpack can't see that import (it doesn't parse inside asset files), so
// force it to also emit this as a static asset alongside the worker.
new URL('maplibre-gl/dist/maplibre-gl-shared.mjs?asset', import.meta.url);

const initialize = function(element, valueAccessor, maplibregl) {
    var defaults = {
        container: element
    };
    var options = ko.unwrap(valueAccessor()).mapOptions || {};
    var mapInitOptions = {};

    _.each(options, function(option, key){
        if (ko.isObservable(option)){
            mapInitOptions[key] = option();
        } else {
            mapInitOptions[key] = option;
        }
    });

    if (mapInitOptions.centerX && mapInitOptions.centerY) {
        mapInitOptions['center'] = [
            mapInitOptions.centerX,
            mapInitOptions.centerY
        ];
    }

    var map = new maplibregl.Map(
        _.defaults(mapInitOptions, defaults)
    );
    window.__mapInstance = map;
    map.on('error', function(e) {
        var err = e && e.error ? e.error : e;
        window.__mapErrors = window.__mapErrors || [];
        window.__mapErrors.push({
            message: err && err.message,
            name: err && err.name,
            status: err && err.status,
            url: err && err.url,
            stack: err && err.stack,
            keys: err ? Object.keys(err) : null,
        });
        console.error('MapLibre error:', err);
    });
    map.on('load', function() {
        _.each(arches.mapMarkers, function(marker) {
            map.loadImage(marker.url).then(function(image) {
                map.addImage(marker.name, image.data);
            }).catch(function(error) {
                throw error;
            });
        });
    });

    // prevents drag events from bubbling
    $(element).mousedown(function(event) {
        event.stopPropagation();
    });

    if (typeof ko.unwrap(valueAccessor()).afterRender === 'function') {
        ko.unwrap(valueAccessor()).afterRender(map);
    }

    if (ko.isObservable(options.zoom)) {
        options.zoom.subscribe(function(val) {
            map.setZoom(val);
        }, this);
    }

    if (ko.isObservable(options.centerX)) {
        options.centerX.subscribe(function(val) {
            map.setCenter(new maplibregl.LngLat(val, options.centerY()));
        }, this);
    }

    if (ko.isObservable(options.centerY)) {
        options.centerY.subscribe(function(val) {
            map.setCenter(new maplibregl.LngLat(options.centerX(), val));
        }, this);
    }

    if (ko.isObservable(options.pitch)) {
        options.pitch.subscribe(function(val) {
            map.setPitch(val);
        }, this);
    }

    if (ko.isObservable(options.setBearing)) {
        options.bearing.subscribe(function(val) {
            map.setBearing(val);
        }, this);
    }

    ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
        map.remove();
    });
};

ko.bindingHandlers.maplibregl = {
    init: (element, valueAccessor) => {
        initialize(element, valueAccessor, maplibre);
    }
};
ko.bindingHandlers.maplibregl.init = ko.bindingHandlers.maplibregl.init.bind(ko.bindingHandlers.maplibregl);

export default ko.bindingHandlers.maplibregl;
