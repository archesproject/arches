import * as maplibregl from "maplibre-gl";

import {
    THUMBNAIL_HEIGHT_PIXELS,
    THUMBNAIL_WIDTH_PIXELS,
} from "@/arches_vue_components/components/MapComponent/constants.ts";

import type { LngLatLike } from "maplibre-gl";

const OFFSCREEN_OFFSET_PIXELS = -10000;

const thumbnailCache = new Map<string, string>();

export function getCachedBasemapThumbnail(
    styleUrl: string,
): string | undefined {
    return thumbnailCache.get(styleUrl);
}

export async function renderBasemapThumbnail(
    styleUrl: string,
    center: LngLatLike,
    zoom: number,
): Promise<string | null> {
    const cachedThumbnail = thumbnailCache.get(styleUrl);
    if (cachedThumbnail) {
        return cachedThumbnail;
    }

    const container = document.createElement("div");
    Object.assign(container.style, {
        position: "absolute",
        insetInlineStart: `${OFFSCREEN_OFFSET_PIXELS}px`,
        insetBlockStart: "0",
        width: `${THUMBNAIL_WIDTH_PIXELS}px`,
        height: `${THUMBNAIL_HEIGHT_PIXELS}px`,
    });
    document.body.appendChild(container);

    const thumbnailMap = new maplibregl.Map({
        container,
        style: styleUrl,
        center,
        zoom,
        interactive: false,
        attributionControl: false,
        canvasContextAttributes: { preserveDrawingBuffer: true },
    });

    try {
        await new Promise<void>((resolve) => {
            thumbnailMap.once("idle", () => resolve());
            thumbnailMap.once("error", () => resolve());
        });
        const thumbnail = thumbnailMap.getCanvas().toDataURL("image/png");
        thumbnailCache.set(styleUrl, thumbnail);
        return thumbnail;
    } catch (error) {
        console.error("Error rendering basemap thumbnail:", error);
        return null;
    } finally {
        thumbnailMap.remove();
        container.remove();
    }
}
