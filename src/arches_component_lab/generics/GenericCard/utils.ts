import type { AliasedTileData } from "@/arches_component_lab/types.ts";

export function extractFileEntriesFromPayload(
    payload: AliasedTileData,
): { file: File; nodeId: string }[] {
    const collectedEntries: { file: File; nodeId: string }[] = [];

    function traverseObject(
        currentObject: AliasedTileData["aliased_data"],
    ): void {
        for (const [_key, value] of Object.entries(currentObject)) {
            if (value instanceof File) {
                const nodeId = currentObject.node_id;

                if (typeof nodeId === "string") {
                    collectedEntries.push({
                        file: value,
                        nodeId: nodeId,
                    });
                }
            } else if (Array.isArray(value)) {
                for (const arrayItem of value) {
                    if (arrayItem && typeof arrayItem === "object") {
                        traverseObject(
                            arrayItem as unknown as AliasedTileData["aliased_data"],
                        );
                    }
                }
            } else if (value && typeof value === "object") {
                traverseObject(
                    value as unknown as AliasedTileData["aliased_data"],
                );
            }
        }
    }

    traverseObject(payload.aliased_data);
    return collectedEntries;
}
