import _ from 'underscore';
import ko from 'knockout';


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
    this.overlaySelectorClosed = params.overlaySelectorClosed || ko.observable(false);
    this.overlays = params.overlays || ko.observableArray([]);

    this.mapControlsExpanded = ko.observable(false);

    this.mapControlPanels = {
        basemaps: ko.observable(false),
        overlays: ko.observable(true),
        maptools: ko.observable(true),
        legend: ko.observable(true)
    };

    /**
     * toggles between the panels: legend, basemaps, etc
     * @return {null}
     */
    this.toggleMapControlPanels = function(data) {
        var panel = data;
        _.each(self.mapControlPanels, function(panelValue, panelName) {
            panelName === panel ? panelValue(false) : panelValue(true);
            panel === 'overlays' || self.overlaySelectorClosed(true);
        });
    };

    /**
     * toggles the open or closed state of the of the map controls
     * @return {null}
     */
    this.toggleMapTools = function() {
        self.mapControlsExpanded(!self.mapControlsExpanded());
    };

    /**
     * toggles the visibility of the of the map controls and the availability of map controls in a report-template
     * @return {null}
     */
    this.toggleMapControlsVisibility = function() {
        if (self.mapControlsHidden() === true) {
            self.mapControlsHidden(false);
        } else {
            self.mapControlsHidden(true);
        }
    };

    this.moveOverlay = function(overlay, direction) {
        var overlays = ko.utils.unwrapObservable(self.overlays);
        var source = ko.utils.arrayIndexOf(overlays, overlay);
        var target = (direction === 'up') ? source - 1 : source + 1;

        if (target >= 0 && target < overlays.length) {
            self.overlays.valueWillMutate();

            overlays.splice(source, 1);
            overlays.splice(target, 0, overlay);

            self.overlays.valueHasMutated();
        }
    };
};
export default MapControlsViewModel;
