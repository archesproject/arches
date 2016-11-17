define(['knockout'], function(ko) {
    /**
     * A viewmodel used for a generic geocoder
     *
     * @constructor
     * @name MapControlsViewModel
     *
     */
    var MapControlsViewModel = function(params) {
        var self = this;
        this.mapControlsHidden = params.mapControlsHidden || ko.observable(false);
        this.selected = ko.observableArray()
        /**
         * toggles the visibility of the geocoder input in the map widget
         * @return {null}
         */
         this.toggleMapControlsVisibility = function() {
             if (self.mapControlsHidden() === true) {
                 self.mapControlsHidden(false)
             } else {
                 self.mapControlsHidden(true)
             }
         }
    };
    return MapControlsViewModel;
});
