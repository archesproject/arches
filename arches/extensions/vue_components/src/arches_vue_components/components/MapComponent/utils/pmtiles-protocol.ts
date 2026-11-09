import * as maplibregl from "maplibre-gl";
import { Protocol } from "pmtiles";

const PMTILES_PROTOCOL_NAME = "pmtiles";

let isPmtilesProtocolRegistered = false;

// MapLibre keeps one protocol registry per page, shared by every map on it.
export function registerPmtilesProtocol(): void {
    if (isPmtilesProtocolRegistered) {
        return;
    }
    const pmtilesProtocol = new Protocol({ metadata: true });
    maplibregl.addProtocol(PMTILES_PROTOCOL_NAME, pmtilesProtocol.tile);
    isPmtilesProtocolRegistered = true;
}
