import type { Feature } from "geojson";
import type {
    Map as MaplibreMap,
    MapEventType,
    Subscription,
} from "maplibre-gl";

export interface DrawEvent {
    features: Feature[];
}

// "draw.*" are custom events fired by @mapbox/mapbox-gl-draw, not part
// of maplibre-gl's typed MapEventType union.
export function onDrawEvent(
    map: MaplibreMap,
    drawEventName: string,
    listener: (drawEvent: DrawEvent) => void,
): Subscription {
    return map.on(drawEventName as keyof MapEventType, (event: unknown) =>
        listener(event as DrawEvent),
    );
}
