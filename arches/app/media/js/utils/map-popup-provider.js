import ko from 'knockout';
import popupTemplate from 'templates/views/components/map-popup.htm';

const provider = {

    /**
     * Callback to determine if the feature is clickable
     * @param feature Map feature to check
     * @returns <code>true</code> if the feature can be clicked, otherwise <code>false</code>
     */
    isFeatureClickable: function(feature, map) {
        const selectedFeatureIds = ko.unwrap(map.selectedFeatureIds);
        const selectedTool = ko.unwrap(map.selectedTool);
        if ((typeof selectedTool !== 'undefined' && selectedTool !== null) || selectedFeatureIds && selectedFeatureIds.length)
            return false;
        return feature.properties.resourceinstanceid;
    },

    /**
     * Return the template that should be used for the popup
     * @param features - Unused in this provider, but may be used in custom provider to determine which template
     * to use
     * @returns {*} HTML template for the Map Popup
     */
    getPopupTemplate: function(features) {
        return popupTemplate;
    },

    /**
     * Each feature in the list must have a <code>displayname</code> and <code>map_popup</code> value. This is
     * handled for arches resources by the framework, but can be injected here if any of the features.popupFeatures
     * do not have one.
     */
    processData: function(features) {
        return features;
    },

    /**
     * This method enables custom logic for how the feature in the popup should be handled and/or mutated en route to the mapFilter.
     * @param popupFeatureObject - the javascript object of the feature and its associated contexts (e.g. mapCard).
     * @required @method mapCard.filterByFeatureGeom()
     * @required @send argument: @param feature - a geojson feature object 
     */
    sendFeatureToMapFilter: function(popupFeatureObject) {
        const foundFeature = this.findPopupFeatureById(popupFeatureObject);
        popupFeatureObject.mapCard.filterByFeatureGeom(foundFeature);
    },

    /**
     * Determines whether to show the button for Filter By Feature
     * @param popupFeatureObject - the javascript object of the feature and its associated contexts (e.g. mapCard).
     * @returns {boolean} - whether to show "Filter by Feature" on map popup
     * typically dependent on at least 1 feature with a geometry and/or a featureid/resourceid combo
     */
    showFilterByFeature: function(popupFeatureObject) {
        const noFeatureId = popupFeatureObject.feature?.properties?.featureid === undefined;
        if (noFeatureId) 
            return false;
        return this.findPopupFeatureById(popupFeatureObject) !== null;
    },

    findPopupFeatureById: function(popupFeatureObject) {
        let foundFeature = null;
        const strippedFeatureId = popupFeatureObject.feature.properties.featureid.replace(/-/g, "");
        for (let geometry of popupFeatureObject.geometries()) {
            if (geometry.geom && Array.isArray(geometry.geom.features)) {
                foundFeature = geometry.geom.features.find(feature => feature.id.replace(/-/g, "") === strippedFeatureId);
                if (foundFeature)
                    break;
            }
        }
        return foundFeature;
    },

};

export default provider;
