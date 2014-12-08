require([
    'jquery',
    'openlayers',
    'bootstrap',
    'select2',
    'plugins/jquery.knob.min'
], function($, ol) {
      //OpenLayer 3 CRUD
  //
  var projection = ol.proj.get('EPSG:3857');


  var styles = [
    'Road',
    'AerialWithLabels',
    'ordnanceSurvey'
  ];

  var layers = [];
  var i, ii;
  for (i = 0, ii = styles.length; i < ii; ++i) {
    layers.push(new ol.layer.Tile({
      visible: false,
      preload: Infinity,
      source: new ol.source.BingMaps({
        key: 'Ak-dzM4wZjSqTlzveKz5u0d4IQ4bRzVI309GxmkgSVr1ewS6iPSrOvOKhA-CJlm3',
        imagerySet: styles[i]
      })
    }));
  }


  //set default map style to Roads
  layers[0].setVisible(true);


  //set up basemap display selection
  $(".basemap").click(function (){ 
      
      var basemap = $(this).attr('id');

      //iterate through the set of layers.  Set the layer visibilty to "true" for the 
      //layer that matches the user's selection
      var i, ii;
        for (i = 0, ii = layers.length; i < ii; ++i) {
          layers[i].setVisible(styles[i] == basemap);
      }

      //close panel
      $("#inventory-home").click();

      //keep page from re-loading
      return false;

  }); 


  var styleFunction = new ol.style.Style({
      fill: new ol.style.Fill({
        color: 'rgba(92, 184, 92, 0.5)'
      }),
      stroke: new ol.style.Stroke({
        color: '#0ff',
        width: 1
      })
    });


  var dragAndDropInteraction = new ol.interaction.DragAndDrop({
    formatConstructors: [
      ol.format.GPX,
      ol.format.GeoJSON,
      ol.format.IGC,
      ol.format.KML,
      ol.format.TopoJSON
    ]
  });


  dragAndDropInteraction.on('addfeatures', function(event) {
    var vectorSource = new ol.source.Vector({
      features: event.features,
      projection: event.projection
    });
    map.getLayers().push(new ol.layer.Vector({
      source: vectorSource,
      style: styleFunction
    }));
    var view = map.getView();
    view.fitExtent(
        vectorSource.getExtent(), /** @type {ol.Size} */ (map.getSize()));
  });


  //Add "inventory" 
  var inventory = new ol.layer.Vector({
        source: new ol.source.KML({
          projection: projection,
          url: 'data/wolfenstein.kml'
        }),
        style: new ol.style.Style({
          stroke: new ol.style.Stroke({
            color: '#555',
            width: 4
          }),
          fill: new ol.style.Fill({
            color: "rgba(40, 170, 68, 0.6)"
          })
        })
      });



  var map = new ol.Map({
    layers: layers,
      interactions: ol.interaction.defaults({
      altShiftDragRotate: false,
      dragPan: false,
      rotate: false
      }).extend([new ol.interaction.DragPan({kinetic: null})]).extend([dragAndDropInteraction]),
    target: 'map',
    view: new ol.View({
      center: [-13168799.0, 4012635.2],
      zoom: 10
    })
  });



  // The features are not added to a regular vector layer/source,
  // but to a feature overlay which holds a collection of features.
  // This collection is passed to the modify and also the draw
  // interaction, so that both can add or modify features.
  var featureOverlay = new ol.FeatureOverlay({
    style: new ol.style.Style({
      fill: new ol.style.Fill({
        color: 'rgba(92, 184, 92, 0.5)'
      }),
      stroke: new ol.style.Stroke({
        color: '#5cb85c',
        width: 2
      }),
      image: new ol.style.Circle({
        radius: 7,
        fill: new ol.style.Fill({
          color: 'rgba(92, 184, 92, 0.5)'
        }),
        stroke: new ol.style.Stroke({
          color: '#5cb85c',
          width: 2
        })
      })
    })
  });
  featureOverlay.setMap(map);


  //Move zoom control so that it isn't under the map search bar
  $(".ol-control").css("margin-top", "70px");


  //End OPenlayer 3 Map









  //Map Tools Buttons... Inventory-home button hides all panels
  $("#inventory-home").click(function (){ 

  //Collapse panels
  $("#overlay-panel").addClass("hidden");
  $("#basemaps-panel").addClass("hidden");

  //Update state of remaining buttons
  $("#inventory-basemaps").removeClass("arches-map-tools-pressed");
  $("#inventory-basemaps").addClass("arches-map-tools");
  $("#inventory-basemaps").css("border-bottom-left-radius", "1px");

  $("#inventory-overlays").removeClass("arches-map-tools-pressed");
  $("#inventory-overlays").addClass("arches-map-tools");
  $("#inventory-overlays").css("border-bottom-right-radius", "1px");


  //Update state of current button and adjust position
  $("#inventory-home").addClass("arches-map-tools-pressed");
  //$("#inventory-home").addClass("button-shim");
  $("#inventory-home").removeClass("arches-map-tools");

  //Don't let the page reload
  return false;

  });

  //Inventory-basemaps button opens basemap panel
  $("#inventory-basemaps").click(function (){ 

  //Collapse panels
  $("#overlay-panel").addClass("hidden");
  $("#basemaps-panel").removeClass("hidden");

  //Update state of remaining buttons
  $("#inventory-home").removeClass("arches-map-tools-pressed");
  $("#inventory-home").addClass("arches-map-tools");

  $("#inventory-overlays").removeClass("arches-map-tools-pressed");
  $("#inventory-overlays").addClass("arches-map-tools");
  $("#inventory-overlays").css("border-bottom-right-radius", "5px");

  //Update state of current button and adjust position
  $("#inventory-basemaps").addClass("arches-map-tools-pressed");
  $("#inventory-basemaps").removeClass("arches-map-tools");
  $("#inventory-basemaps").css("border-bottom-left-radius", "5px");

  //Don't let the page reload
  return false;

  });


  //Inventory-overlayss button opens overlay panel
  $("#inventory-overlays").click(function (){ 

  //Collapse panels
  $("#overlay-panel").removeClass("hidden");
  $("#basemaps-panel").addClass("hidden");

  //Update state of remaining buttons
  $("#inventory-home").removeClass("arches-map-tools-pressed");
  $("#inventory-home").addClass("arches-map-tools");

  $("#inventory-basemaps").removeClass("arches-map-tools-pressed");
  $("#inventory-basemaps").addClass("arches-map-tools");

  //Update state of current button and adjust position
  $("#inventory-overlays").addClass("arches-map-tools-pressed");
  $("#inventory-overlays").removeClass("arches-map-tools");

  //Don't let the page reload
  return false;

  });


  //Close Button
  $(".close").click(function (){ 

  $("#inventory-home").click()

  });


  //Toggle Overlay display
  $(".toggle-overlay").click(function(){

  //Don't let the page reload
  return false;

  });


  //Zoom Overlay 
  $(".zoom").click(function(){

  //Don't let the page reload
  return false;

  });



  //Show and hide Layer Library.  
  $("#add-layer").click(function(){ handleLayerLibary(); return false; });
  $("#back-to-map").click(function(){ handleInventoryMap(); return false; });

  function handleLayerLibary() {    

  //function to toggle display of map div
  $( "#map-panel" ).slideToggle(600);
  $( "#layer-library" ).slideToggle(600);

  }

  function handleInventoryMap() {    

  //function to toggle display of map div
  $( "#map-panel" ).slideToggle(600);
  $( "#layer-library" ).slideToggle(600);

  }



  //Select2 Simple Search initialize
  $('.layerfilter').select2({
  data: function() {
  var data;

  data = [
  {id: "administrative", text: "Administrative Layers"},
  {id: "environmental", text: "Environmental Layers"},
  {id: "planning", text: "Planning Layers"},
  {id: "historical", text: "Historical Maps"},
  {id: "heritage", text: "Cultural Heritage Maps"},
  ];

  return {results:data};
  },
  placeholder: "Filter Layer List",
  multiple: true,
  maximumSelectionSize: 5

  });

  //filter layer library
  $(".layerfilter").on("select2-selecting", function(e) {

  //alert("selecting val=" + e.val + " choice=" + e.object.text);
  //toggle off layers that don't match the users' selection
  var selected = e.val;

  if (selected == 'historical') {
      //toggle off layers that arent historical
      $(".administrative").toggle(600);
      $(".heritage").toggle(600);

  };
  })

  $(".layerfilter").on("select2-removed", function(e) {

  //alert("selecting val=" + e.val + " choice=" + e.object.text);
  //toggle off layers that don't match the users' selection
  var unselected = e.val;

  if (unselected == 'historical') {
      //toggle off layers that arent historical
      $(".administrative").toggle(600);
      $(".heritage").toggle(600);

  };

  })


  //Layer Selector
  $(".layer-selector").click (function(event){ handleLayerSelection(); return false; });

  function handleLayerSelection() {    

  //determine which layer user wants to enable/disable.  Determine layer by trimming "-button" from url, its icon
  //by adding -icon to layer name, and its thumbnail by adding -img to layer name
  var layer_url = "#" + event.target.id;
  var layer = layer_url.slice(0, -7);
  var icon = layer + "-icon";
  var thumb = layer + "-img";
  var knobs = layer + "-knobs";


  if ($(layer).hasClass("arches-ll-selected")) {

      //user wants to remove layer from map
      $(layer).removeClass("arches-ll-selected");
      $(icon).removeClass("fa-dot-circle-o");
      $(icon).addClass("fa-ban");
      $(thumb).css("opacity", "0.5");
      $(layer_url).removeClass("layer-selected-title");
      $(knobs).css("display", "none");

      } else {

          //User wants to add layer to map
          $(layer).addClass("arches-ll-selected");
          $(icon).addClass("fa-dot-circle-o");
          $(icon).removeClass("fa-ban");
          $(thumb).css("opacity", "1");
          $(layer_url).addClass("layer-selected-title");
          $(knobs).css("display", "block");

  }

  }



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
  {id: "7", text: "Parcel: 13-012-987"},  
  ];

  return {results:data};
  },
  placeholder: "Find an Address or Parcel Number",
  multiple: true,
  maximumSelectionSize: 1
  });


  /*
  * KNOB
  */

  $('.knob').knob({

      //displayInput: false,

      change: function (value) {
          //console.log("change : " + value);
      },
      release: function (value) {
          //console.log(this.$.attr('value'));
          //console.log("release : " + value);
      },
      cancel: function () {
          //console.log("cancel : ", this);
      }
  });

  //Knob overrides
  $(".knob").css("font-size", 11);
  $(".knob").css("font-weight", 200);


  //Position OpenLayers COntrol
  $(".ol-zoom").css("top", "70px");

});