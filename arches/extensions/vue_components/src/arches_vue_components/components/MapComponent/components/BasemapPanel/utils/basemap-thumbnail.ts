import * as maplibregl from "maplibre-gl";

import type { LngLatLike } from "maplibre-gl";

const cachedThumbnailsByStyleUrl = new Map<string, string>();

export async function renderBasemapThumbnail(
    container: HTMLElement,
    styleUrl: string,
    center: LngLatLike,
    zoom: number,
): Promise<string | null> {
    const cachedThumbnail = cachedThumbnailsByStyleUrl.get(styleUrl);
    if (cachedThumbnail) {
        return cachedThumbnail;
    }

    const thumbnailRenderer = new maplibregl.Map({
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
            thumbnailRenderer.once("idle", () => resolve());
            thumbnailRenderer.once("error", () => resolve());
        });
        const thumbnail = thumbnailRenderer.getCanvas().toDataURL("image/png");
        cachedThumbnailsByStyleUrl.set(styleUrl, thumbnail);
        return thumbnail;
    } catch (error) {
        console.error("Error rendering basemap thumbnail:", error);
        return null;
    } finally {
        thumbnailRenderer.remove();
    }
}
