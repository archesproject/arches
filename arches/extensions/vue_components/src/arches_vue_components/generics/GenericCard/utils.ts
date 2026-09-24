import type {
    AliasedData,
    AliasedNodeData,
    FileEntry,
} from "@/arches_vue_components/types.ts";

export function isAliasedNodeData(value: unknown): value is AliasedNodeData {
    return (
        value !== null &&
        value !== undefined &&
        typeof value === "object" &&
        "node_value" in value &&
        "display_value" in value &&
        "details" in value
    );
}

export function extractAliasedNodeDataEntries(
    data: Record<string, unknown>,
): Record<string, AliasedNodeData> {
    return Object.fromEntries(
        Object.entries(data)
            .filter(([, rawNodeData]) => isAliasedNodeData(rawNodeData))
            .map(([nodeAlias, rawNodeData]) => [
                nodeAlias,
                rawNodeData as AliasedNodeData,
            ]),
    );
}

export function extractFileEntriesFromAliasedData(
    payload: AliasedData,
): FileEntry[] {
    const collectedEntries: FileEntry[] = [];

    function traverseObject(
        currentObject: AliasedData,
        currentTileId: string | null,
    ): void {
        if (
            "tileid" in currentObject &&
            typeof currentObject.tileid === "string"
        ) {
            currentTileId = currentObject.tileid;
        }

        for (const value of Object.values(currentObject)) {
            if (value instanceof File) {
                const nodeId = currentObject.node_id;

                if (typeof nodeId === "string") {
                    collectedEntries.push({
                        file: value,
                        nodeId: nodeId,
                        tileId: currentTileId,
                    });
                }
            } else if (Array.isArray(value)) {
                for (const arrayItem of value) {
                    if (arrayItem && typeof arrayItem === "object") {
                        traverseObject(
                            arrayItem as unknown as AliasedData,
                            currentTileId,
                        );
                    }
                }
            } else if (value && typeof value === "object") {
                traverseObject(value as unknown as AliasedData, currentTileId);
            }
        }
    }

    traverseObject(payload, null);
    return collectedEntries;
}

export function buildFileUploadFormData(
    payload: unknown,
    fileEntries: FileEntry[],
): FormData {
    const formData = new FormData();
    formData.append("json", JSON.stringify(payload));

    for (const { file, nodeId, tileId } of fileEntries) {
        let fieldName = `file-list_${nodeId}`;
        if (tileId) {
            fieldName = `file-list_${tileId}-${nodeId}`;
        }
        formData.append(fieldName, file, file.name);
    }

    return formData;
}
