/**
 * Default geocoderApi for the maplibre-gl-geocoder control used on the
 * map search page. Backed by the free OpenStreetMap Nominatim service so
 * that no API key is required out of the box.
 *
 * Projects that want a different geocoding backend (e.g. Mapbox,
 * MapTiler, an in-house service) can override this file at the same
 * path to swap in their own `forwardGeocode` implementation and update
 * `geocoderAttribution` to match, without touching `viewmodels/map.js`.
 *
 * Nominatim's usage policy (https://operations.osmfoundation.org/policies/nominatim/)
 * requires visible attribution of OpenStreetMap/ODbL data; `geocoderAttribution`
 * is surfaced in the map's AttributionControl for this reason.
 */
const NOMINATIM_SEARCH_URL = 'https://nominatim.openstreetmap.org/search';

export const geocoderAttribution = 'Geocoding by <a href="https://nominatim.org" target="_blank">Nominatim</a>';

const toCarmenFeature = function(feature) {
    return {
        id: feature.properties.place_id,
        type: 'Feature',
        text: feature.properties.name || feature.properties.display_name,
        place_name: feature.properties.display_name,
        place_type: [feature.properties.type],
        bbox: feature.bbox,
        center: feature.geometry.coordinates,
        geometry: feature.geometry,
    };
};

const maplibreGeocoderApi = {
    forwardGeocode: async function(config) {
        const params = new URLSearchParams({
            format: 'geojson',
            q: config.query,
            limit: config.limit || 5,
        });

        if (config.bbox) {
            params.set('viewbox', config.bbox.join(','));
            params.set('bounded', '1');
        }

        try {
            const response = await fetch(`${NOMINATIM_SEARCH_URL}?${params.toString()}`);
            const geojson = await response.json();
            return {
                type: 'FeatureCollection',
                features: geojson.features.map(toCarmenFeature),
            };
        } catch (error) {
            console.error(error);
            return { type: 'FeatureCollection', features: [] };
        }
    },
};

export default maplibreGeocoderApi;
