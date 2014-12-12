require([
    'jquery',
    'underscore',
    'openlayers',
    'knockout',
    'arches',
    'views/map',
    'map/layers',
    'bootstrap',
    'select2',
    'plugins/jquery.knob.min'
], function($, _, ol, ko, arches, MapView, layers) {
    var mapLayers = [];
    _.each(layers, function(layer, index) {
        if (layer.onMap) {
            mapLayers.push(layer.layer);
        }
        layer.onMap = ko.observable(layer.onMap);
        layers[index].onMap.subscribe(function(add) {
            if (add) {
                map.map.addLayer(layer.layer);
            } else {
                map.map.removeLayer(layer.layer);
            }
        });
        layer.active = ko.observable(true);
        layers[index].active.subscribe(function(show) {
            layer.layer.setVisible(show);
        });
    });
    var map = new MapView({
        el: $('#map'),
        overlays: mapLayers
    });
    var viewModel = {
        baseLayers: map.baseLayers,
        layers: ko.observableArray(layers),
        filterTerms: ko.observableArray()
    };

    viewModel.filteredLayers = ko.computed(function() {
        if(viewModel.filterTerms().length == 0) {
            return viewModel.layers();
        } else {
            return ko.utils.arrayFilter(viewModel.layers(), function(layer) {
                var include = false;
                _.each(viewModel.filterTerms(), function(term) {
                    if (term.text === layer.name) {
                        include = true;
                    } else if (_.contains(layer.categories, term.text)) {
                        include = true;
                    }
                });
                return include
            });
        }
    });

    var hideAllPanels = function () {
        $("#overlay-panel").addClass("hidden");
        $("#basemaps-panel").addClass("hidden");

        //Update state of remaining buttons
        $("#inventory-basemaps").removeClass("arches-map-tools-pressed");
        $("#inventory-basemaps").addClass("arches-map-tools");
        $("#inventory-basemaps").css("border-bottom-left-radius", "1px");

        $("#inventory-overlays").removeClass("arches-map-tools-pressed");
        $("#inventory-overlays").addClass("arches-map-tools");
        $("#inventory-overlays").css("border-bottom-right-radius", "1px");
    };

    ko.applyBindings(viewModel, $('body')[0]);

    $(".basemap").click(function (){ 
        var basemap = $(this).attr('id');
        _.each(map.baseLayers, function(baseLayer){ 
            baseLayer.layer.setVisible(baseLayer.id == basemap);
        });
        hideAllPanels();
    });

    //Inventory-basemaps button opens basemap panel
    $("#inventory-basemaps").click(function (){
        $("#overlay-panel").addClass("hidden");
        $("#basemaps-panel").removeClass("hidden");

        //Update state of remaining buttons
        $("#inventory-overlays").removeClass("arches-map-tools-pressed");
        $("#inventory-overlays").addClass("arches-map-tools");
        $("#inventory-overlays").css("border-bottom-right-radius", "5px");

        //Update state of current button and adjust position
        $("#inventory-basemaps").addClass("arches-map-tools-pressed");
        $("#inventory-basemaps").removeClass("arches-map-tools");
        $("#inventory-basemaps").css("border-bottom-left-radius", "5px");
    });


    //Inventory-overlayss button opens overlay panel
    $("#inventory-overlays").click(function (){
        $("#overlay-panel").removeClass("hidden");
        $("#basemaps-panel").addClass("hidden");

        //Update state of remaining buttons
        $("#inventory-basemaps").removeClass("arches-map-tools-pressed");
        $("#inventory-basemaps").addClass("arches-map-tools");

        //Update state of current button and adjust position
        $("#inventory-overlays").addClass("arches-map-tools-pressed");
        $("#inventory-overlays").removeClass("arches-map-tools");
    });

    //Close Button
    $(".close").click(function (){ 
        hideAllPanels();
    });

    //Show and hide Layer Library.  
    $("#add-layer").click(function(){
        $( "#map-panel" ).slideToggle(600);
        $( "#layer-library" ).slideToggle(600);
    });

    $("#back-to-map").click(function(){
        $( "#map-panel" ).slideToggle(600);
        $( "#layer-library" ).slideToggle(600);
    });

    $(".visibility-toggle").click (function(event){
        var layerId = $(this).data().layerid;
        
        layer = ko.utils.arrayFirst(viewModel.layers(), function(item) {
            return layerId === item.id;
        });

        layer.active(!layer.active());
    });

    $('.layer-zoom').click(function () {
        var layerId = $(this).data().layerid;
        var layer = ko.utils.arrayFirst(viewModel.layers(), function(item) {
            return layerId === item.id;
        });
        map.map.getView().fitExtent(layer.layer.getSource().getExtent(), map.map.getSize());
    });


    $('.knob').knob({
        change: function (value) {
            var layerId = this.$.data().layerid;
            var layer = ko.utils.arrayFirst(viewModel.layers(), function(item) {
                return layerId === item.id;
            });
            layer.layer.setOpacity(value/100)
        }
    });
    $(".knob").css("font-size", 11);
    $(".knob").css("font-weight", 200);

    $(".ol-zoom").css("top", "70px");

    $('.on-map-toggle').click(function () {
        var layerId = $(this).data().layerid;
        
        layer = ko.utils.arrayFirst(viewModel.layers(), function(item) {
            return layerId === item.id;
        });

        layer.onMap(!layer.onMap());
    });

    //Select2 Simple Search initialize
    $('.layerfilter').select2({
        data: function() {
            var terms = [];
            _.each(layers, function (layer) {
                terms = _.union(terms, layer.categories, [layer.name]);
            });

            return {
                results: _.map(terms, function(term) { 
                    return {
                        id: _.uniqueId('term'),
                        text: term
                    }
                })
            };
        },
        placeholder: "Filter Layer List",
        multiple: true,
        maximumSelectionSize: 5
    });

    //filter layer library
    $(".layerfilter").on("select2-selecting", function(e) {
        viewModel.filterTerms.push(e.object);
    });

    $(".layerfilter").on("select2-removed", function(e) {
        var term = ko.utils.arrayFirst(viewModel.filterTerms(), function(term) {
            return term.id === e.val;
        });

        viewModel.filterTerms.remove(term);
    });

    //Select2 Simple Search initialize
    $('.geocodewidget').select2({
        data: function() {
            var data;

            data = [
                {id: "1", text: "109 Newhaven Street, Los Angeles, CA"},
                {id: "2", text: "11243 Western Drive Los Angeles, CA"},
                {id: "3", text: "2566 Alison Drive, Santa Monica, CA"},
                {id: "4", text: "34789 Myers Circle, Burbank, CA"},
                {id: "5", text: "Parcel: 110-445-009"},
                {id: "6", text: "Parcel: 333-012-987"},
                {id: "7", text: "Parcel: 13-012-987"}
            ];

            return {results: data};
        },
        placeholder: "Find an Address or Parcel Number",
        multiple: true,
        maximumSelectionSize: 1
    });

});