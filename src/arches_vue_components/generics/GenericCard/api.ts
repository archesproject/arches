import Cookies from "js-cookie";

import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";

import {
    buildFileUploadFormData,
    extractFileEntriesFromAliasedData,
} from "@/arches_vue_components/generics/GenericCard/utils.ts";

import type {
    AliasedTileData,
    FileEntry,
} from "@/arches_vue_components/types.ts";

export async function fetchTileData(
    graphSlug: string,
    nodegroupAlias: string,
    tileId?: string | null | undefined,
): Promise<AliasedTileData> {
    let tileUrl;

    if (tileId) {
        tileUrl = generateArchesURL("arches_querysets:api-tile", {
            graph: graphSlug,
            nodegroup_alias: nodegroupAlias,
            pk: tileId,
        });
    } else {
        tileUrl = generateArchesURL("arches_querysets:api-tile-blank", {
            graph: graphSlug,
            nodegroup_alias: nodegroupAlias,
        });
    }

    const response = await fetch(tileUrl);
    const parsed = await response.json();

    if (!response.ok) {
        throw new Error(parsed.message ?? response.statusText);
    }
    return parsed;
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
    let endpointUrl;

    if (tileId) {
        endpointUrl = generateArchesURL("arches_querysets:api-tile", {
            graph: graphSlug,
            nodegroup_alias: nodegroupAlias,
            pk: tileId,
        });
    } else if (resourceInstanceId) {
        endpointUrl = generateArchesURL(
            "arches_querysets:api-tile-list-create",
            {
                graph: graphSlug,
                nodegroup_alias: nodegroupAlias,
                pk: resourceInstanceId,
            },
        );
    } else {
        endpointUrl = generateArchesURL(
            "arches_querysets:api-tile-new-resource",
            {
                graph: graphSlug,
                nodegroup_alias: nodegroupAlias,
            },
        );
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
    fileEntries: FileEntry[],
    tileId?: string,
    resourceInstanceId?: string | null,
): Promise<AliasedTileData> {
    let endpointUrl;

    if (tileId) {
        endpointUrl = generateArchesURL("arches_querysets:api-tile", {
            graph: graphSlug,
            nodegroup_alias: nodegroupAlias,
            pk: tileId,
        });
    } else if (resourceInstanceId) {
        endpointUrl = generateArchesURL(
            "arches_querysets:api-tile-list-create",
            {
                graph: graphSlug,
                nodegroup_alias: nodegroupAlias,
                pk: resourceInstanceId,
            },
        );
    } else {
        endpointUrl = generateArchesURL(
            "arches_querysets:api-tile-new-resource",
            {
                graph: graphSlug,
                nodegroup_alias: nodegroupAlias,
            },
        );
    }

    const httpMethod = tileId ? "PATCH" : "POST";
    const response = await fetch(endpointUrl, {
        method: httpMethod,
        headers: {
            // It's important to not set 'Content-Type' here, as the browser will set it automatically
            // with the correct boundary for multipart/form-data.
            "X-CSRFTOKEN": Cookies.get("csrftoken"),
        },
        body: buildFileUploadFormData(payload, fileEntries),
    });

    const parsedBody = await response.json();
    if (!response.ok) {
        throw new Error(parsedBody.message || response.statusText);
    }
    return parsedBody;
}
