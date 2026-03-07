import arches from "arches";
import Cookies from "js-cookie";

import { extractFileEntriesFromAliasedData } from "@/arches_component_lab/generics/GenericCard/utils.ts";

import type {
    AliasedTileData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";

export async function fetchTileData(
    graphSlug: string,
    nodegroupAlias: string,
    tileId?: string | null | undefined,
): Promise<AliasedTileData> {
    let tileUrl;

    if (tileId) {
        tileUrl = arches.urls.api_tile(graphSlug, nodegroupAlias, tileId);
    } else {
        tileUrl = arches.urls.api_tile_blank(graphSlug, nodegroupAlias);
    }

    const response = await fetch(tileUrl);
    const parsed = await response.json();

    if (!response.ok) {
        throw new Error(parsed.message ?? response.statusText);
    }
    return parsed;
}

// Promise-based cache: graph config is static for the lifetime of the SPA.
const nodegroupConfigCache = new Map<string, Promise<CardXNodeXWidgetData[]>>();

async function fetchCardXNodeXWidgetDataFromNodeGroupFromServer(
    graphSlug: string,
    nodegroupAlias: string,
): Promise<CardXNodeXWidgetData[]> {
    const response = await fetch(
        arches.urls.api_card_x_node_x_widget_list_from_nodegroup(
            graphSlug,
            nodegroupAlias,
        ),
    );
    const parsed = await response.json();
    if (!response.ok) {
        throw new Error(parsed.message ?? response.statusText);
    }
    return parsed;
}

export function fetchCardXNodeXWidgetDataFromNodeGroup(
    graphSlug: string,
    nodegroupAlias: string,
): Promise<CardXNodeXWidgetData[]> {
    const cacheKey = `${graphSlug}:${nodegroupAlias}`;

    if (!nodegroupConfigCache.has(cacheKey)) {
        const fetchRequest = fetchCardXNodeXWidgetDataFromNodeGroupFromServer(
            graphSlug,
            nodegroupAlias,
        );

        // On failure, evict so a retry can re-fetch.
        fetchRequest.catch(() => nodegroupConfigCache.delete(cacheKey));
        nodegroupConfigCache.set(cacheKey, fetchRequest);
    }

    return nodegroupConfigCache.get(cacheKey)!;
}

export async function upsertTile(
    graphSlug: string,
    nodegroupAlias: string,
    payload: AliasedTileData,
    tileId?: string,
    resourceInstanceId?: string | null | undefined,
): Promise<AliasedTileData> {
    const fileEntries = extractFileEntriesFromAliasedData(payload.aliased_data);

    if (fileEntries.length > 0) {
        return upsertTileWithFiles(
            graphSlug,
            nodegroupAlias,
            payload,
            fileEntries,
            tileId,
            resourceInstanceId,
        );
    }
    return upsertTileAsJson(
        graphSlug,
        nodegroupAlias,
        payload,
        tileId,
        resourceInstanceId,
    );
}

// TODO: DRY this when functionality lands
export async function upsertTileAsJson(
    graphSlug: string,
    nodegroupAlias: string,
    payload: AliasedTileData,
    tileId?: string,
    resourceInstanceId?: string | null | undefined,
): Promise<AliasedTileData> {
    const urlSegments = [graphSlug, nodegroupAlias];
    let endpointUrl;

    if (tileId) {
        urlSegments.push(tileId);
        endpointUrl = arches.urls.api_tile(...urlSegments);
    } else if (resourceInstanceId) {
        urlSegments.push(resourceInstanceId);
        endpointUrl = arches.urls.api_tile_list_create(...urlSegments);
    } else {
        endpointUrl = arches.urls.api_tile_new_resource(...urlSegments);
    }

    const httpMethod = tileId ? "PATCH" : "POST";

    const response = await fetch(endpointUrl, {
        method: httpMethod,
        headers: {
            "Content-Type": "application/json",
            "X-CSRFTOKEN": Cookies.get("csrftoken"),
        },
        body: JSON.stringify(payload),
    });

    const parsedBody = await response.json();
    if (!response.ok) {
        throw new Error(parsedBody.message || response.statusText);
    }
    return parsedBody;
}

// TODO: DRY this when functionality lands
export async function upsertTileWithFiles(
    graphSlug: string,
    nodegroupAlias: string,
    payload: AliasedTileData,
    fileEntries: Array<{ file: File; nodeId: string }>,
    tileId?: string,
    resourceInstanceId?: string | null,
): Promise<AliasedTileData> {
    const urlSegments = [graphSlug, nodegroupAlias];
    let endpointUrl;

    if (tileId) {
        urlSegments.push(tileId);
        endpointUrl = arches.urls.api_tile(...urlSegments);
    } else if (resourceInstanceId) {
        urlSegments.push(resourceInstanceId);
        endpointUrl = arches.urls.api_tile_list_create(...urlSegments);
    }

    const formData = new FormData();
    formData.append("json", JSON.stringify(payload));

    for (const { file, nodeId } of fileEntries) {
        formData.append(`file-list_${nodeId}`, file, file.name);
    }

    const httpMethod = tileId ? "PATCH" : "POST";
    const response = await fetch(endpointUrl, {
        method: httpMethod,
        headers: {
            // It's important to not set 'Content-Type' here, as the browser will set it automatically
            // with the correct boundary for multipart/form-data.
            "X-CSRFTOKEN": Cookies.get("csrftoken"),
        },
        body: formData,
    });

    const parsedBody = await response.json();
    if (!response.ok) {
        throw new Error(parsedBody.message || response.statusText);
    }
    return parsedBody;
}
