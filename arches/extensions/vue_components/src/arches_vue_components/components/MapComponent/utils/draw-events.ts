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
function toMapEventName(drawEventName: string): keyof MapEventType {
    return drawEventName as keyof MapEventType;
}

export function onDrawEvent(
    map: MaplibreMap,
    drawEventName: string,
    listener: (drawEvent: DrawEvent) => void,
): Subscription {
    return map.on(toMapEventName(drawEventName), (event: unknown) =>
        listener(event as DrawEvent),
    );
}

export function fireDrawEvent(
    map: MaplibreMap,
    drawEventName: string,
    drawEvent?: DrawEvent,
): void {
    map.fire(toMapEventName(drawEventName), drawEvent);
}
