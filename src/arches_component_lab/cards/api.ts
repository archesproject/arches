import arches from "arches";
import Cookies from "js-cookie";

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

export const upsertTile = async (
    graphSlug: string,
    nodegroupAlias: string,
    payload: Record<string, unknown>,
    tileId?: string,
) => {
    // 1) URL + method
    const urlSegments = [graphSlug, nodegroupAlias];
    if (tileId) {
        urlSegments.push(tileId);
    }
    const requestUrl = arches.urls.api_tile(...urlSegments);
    const requestMethod = tileId ? "PUT" : "POST";

    // 2) CSRF
    const headers: Record<string, string> = {
        "X-CSRFTOKEN": Cookies.get("csrftoken") || "",
        // ← no Content-Type here
    };

    // 3) Clone + strip Files
    const clonedPayload = structuredClone(payload);
    type UploadEntry = { file: File; node_id: string };
    const filesToUpload: UploadEntry[] = [];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (function extractFiles(obj: any) {
        for (const key of Object.keys(obj)) {
            const value = obj[key];
            if (value instanceof File) {
                filesToUpload.push({ file: value, node_id: obj.node_id });
                delete obj[key];
            } else if (value && typeof value === "object") {
                extractFiles(value);
            }
        }
    })(clonedPayload);

    // 4) Build FormData
    const formData = new FormData();
    // — append the JSON on the key the API wants
    formData.append("json", JSON.stringify(clonedPayload));
    // — append each file
    filesToUpload.forEach(({ file, node_id }) => {
        formData.append(`file-list_${node_id}`, file, file.name);
    });

    // 5) Fire the request as multipart
    const response = await fetch(requestUrl, {
        method: requestMethod,
        headers, // only X-CSRFTOKEN
        body: formData,
    });

    // 6) Parse + error‐wrap
    const rawText = await response.text();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let parsed: any = {};
    try {
        if (rawText) {
            parsed = JSON.parse(rawText);
        }
    } catch {
        throw new Error(response.statusText);
    }
    if (response.ok) {
        return parsed;
    }
    throw new Error(parsed.message || response.statusText);
};
