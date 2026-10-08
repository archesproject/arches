import type { Feature, Point } from "geojson";
import type {
    CarmenGeojsonFeature,
    MaplibreGeocoderApi,
    MaplibreGeocoderApiConfig,
    MaplibreGeocoderFeatureResults,
} from "@maplibre/maplibre-gl-geocoder";

const NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search";
const DEFAULT_RESULT_LIMIT = 5;

export const GEOCODER_ATTRIBUTION =
    'Geocoding by <a href="https://nominatim.org" target="_blank">Nominatim</a>';

interface NominatimProperties {
    place_id: number;
    name?: string;
    display_name: string;
    type: string;
}

interface NominatimFeature extends Feature<Point, NominatimProperties> {
    bbox?: [number, number, number, number];
}

function toCarmenFeature(feature: NominatimFeature): CarmenGeojsonFeature {
    const [longitude, latitude] = feature.geometry.coordinates;

    return {
        id: String(feature.properties.place_id),
        type: "Feature",
        text: feature.properties.name || feature.properties.display_name,
        place_name: feature.properties.display_name,
        place_type: [feature.properties.type],
        bbox: feature.bbox,
        center: [longitude, latitude],
        geometry: feature.geometry,
        properties: {},
    };
}

async function forwardGeocode(
    config: MaplibreGeocoderApiConfig,
): Promise<MaplibreGeocoderFeatureResults> {
    const params = new URLSearchParams({
        format: "geojson",
        q: String(config.query),
        limit: String(config.limit ?? DEFAULT_RESULT_LIMIT),
    });

    if (config.bbox) {
        params.set("viewbox", config.bbox.join(","));
        params.set("bounded", "1");
    }

    try {
        const response = await fetch(
            `${NOMINATIM_SEARCH_URL}?${params.toString()}`,
        );
        const geojson: { features: NominatimFeature[] } = await response.json();
        return {
            type: "FeatureCollection",
            features: geojson.features.map(toCarmenFeature),
        };
    } catch (error) {
        console.error(error);
        return { type: "FeatureCollection", features: [] };
    }
}

export const nominatimGeocoderApi: MaplibreGeocoderApi = { forwardGeocode };
