import type { AliasedTileData } from "@/arches_component_lab/cards/types.ts";

export function extractFileEntriesFromPayload(
    payload: AliasedTileData,
): { file: File; nodeId: string }[] {
    const collectedEntries: { file: File; nodeId: string }[] = [];

    function traverseObject(currentObject: AliasedTileData): void {
        if (!currentObject.aliased_data) return;

        for (const [_key, value] of Object.entries(currentObject)) {
            if (value instanceof File) {
                const maybeNodeId = currentObject.node_id;
                if (typeof maybeNodeId === "string") {
                    collectedEntries.push({
                        file: value,
                        nodeId: maybeNodeId,
                    });
                }
            } else if (Array.isArray(value)) {
                for (const arrayItem of value) {
                    if (arrayItem && typeof arrayItem === "object") {
                        traverseObject(arrayItem as AliasedTileData);
                    }
                }
            } else if (value && typeof value === "object") {
                traverseObject(value as AliasedTileData);
            }
        }
    }

    traverseObject(payload);
    return collectedEntries;
}
