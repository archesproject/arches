define(['arches'], function(arches) {
    return {
        "version": 8,
        "name": "Basic",
        "metadata": {
            "mapbox:autocomposite": true,
            "mapbox:type": "template"
        },
        "sources": arches.mapSources,
        "sprite": "mapbox://sprites/mapbox/basic-v9",
        "glyphs": "mapbox://fonts/mapbox/{fontstack}/{range}.pbf",
        "layers": []
    };
});
