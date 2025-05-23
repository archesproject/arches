import arches from "arches";
import Cookies from "js-cookie";

export const fetchCardData = async (
    graphSlug: string,
    nodegroupGroupingNodeAlias: string,
) => {
    const response = await fetch(
        arches.urls.api_card_data(graphSlug, nodegroupGroupingNodeAlias),
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
    nodegroupGroupingNodeAlias: string,
    tileId: string | undefined,
) => {
    const response = await fetch(
        arches.urls.api_tile(graphSlug, nodegroupGroupingNodeAlias, tileId),
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

export const upsertTile = async (
    graphSlug: string,
    nodegroupGroupingNodeAlias: string,
    data: Record<string, unknown>,
    tileId?: string,
) => {
    const args = [graphSlug, nodegroupGroupingNodeAlias];

    if (tileId) {
        args.push(tileId);
    }

    const response = await fetch(arches.urls.api_tile(...args), {
        method: tileId ? "PUT" : "POST",
        body: JSON.stringify(data),
        headers: {
            "X-CSRFTOKEN": Cookies.get("csrftoken"),
            "Content-Type": "application/json",
        },
    });

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
