import arches from "arches";
import Cookies from "js-cookie";

import { extractFileEntriesFromPayload } from "@/arches_component_lab/cards/utils.ts";

export const fetchCardData = async (
    graphSlug: string,
    nodegroupAlias: string,
) => {
    const response = await fetch(
        arches.urls.api_card_data(graphSlug, nodegroupAlias),
    );

    try {
        const parsed = await response.json();
        if (response.ok) {
            return parsed;
        }
        throw new Error(parsed.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const fetchTileData = async (
    graphSlug: string,
    nodegroupAlias: string,
    tileId: string | null | undefined,
) => {
    const response = await fetch(
        arches.urls.api_tile(graphSlug, nodegroupAlias, tileId),
    );

    try {
        const parsed = await response.json();
        if (response.ok) {
            return parsed;
        }
        throw new Error(parsed.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const fetchCardXNodeXWidgetDataFromNodeGroup = async (
    graphSlug: string,
    nodegroupAlias: string,
) => {
    const response = await fetch(
        arches.urls.api_card_x_node_x_widget_list_from_nodegroup(
            graphSlug,
            nodegroupAlias,
        ),
    );

    try {
        const parsed = await response.json();
        if (response.ok) {
            return parsed;
        }
        throw new Error(parsed.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export async function upsertTile(
    graphSlug: string,
    nodegroupAlias: string,
    payload: Record<string, unknown>,
    tileId?: string,
): Promise<unknown> {
    const urlSegments = [graphSlug, nodegroupAlias];
    let httpMethod = "POST";

    if (tileId) {
        urlSegments.push(tileId);
        httpMethod = "PUT";
    }

    const formData = new FormData();
    formData.append("json", JSON.stringify(payload));

    const fileEntries = extractFileEntriesFromPayload(payload);
    for (const { file, nodeId } of fileEntries) {
        formData.append(`file-list_${nodeId}`, file, file.name);
    }

    const endpointUrl = arches.urls.api_tile(...urlSegments);
    const response = await fetch(endpointUrl, {
        method: httpMethod,
        headers: { "X-CSRFTOKEN": Cookies.get("csrftoken") },
        body: formData,
    });

    try {
        const raw = await response.text();
        const parsed = JSON.parse(raw);

        if (response.ok) {
            return parsed;
        }
        throw new Error(parsed.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
}
