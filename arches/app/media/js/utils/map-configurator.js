define([], function(){

    let mapConfigurator = {
        preConfig: function(map) {
            // This can be used to configure the map as the beginning of the map.on('load') event
        },
        postConfig: function(map) {
            // This can be used to configure the map as the end of the map.on('load') event
        },
    };

    return mapConfigurator;
});
