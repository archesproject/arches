import MapboxDraw from "@mapbox/mapbox-gl-draw";

import type { Map as MaplibreMap } from "maplibre-gl";

export function getMapboxDraw(
    map: MaplibreMap,
): InstanceType<typeof MapboxDraw> | undefined {
    return map._controls?.find(
        (control: unknown) => control instanceof MapboxDraw,
    ) as InstanceType<typeof MapboxDraw> | undefined;
}
