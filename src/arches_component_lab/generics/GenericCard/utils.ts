import type { AliasedTileData } from "@/arches_component_lab/generics/GenericCard/types.ts";
import type { AliasedTileNodeValue } from "@/arches_component_lab/types.ts";

export function extractFileEntriesFromPayload(
    payload: AliasedTileData,
): { file: File; nodeId: string }[] {
    const collectedEntries: { file: File; nodeId: string }[] = [];

    function traverseObject(currentObject: {
        [key: string]: AliasedTileNodeValue;
    }): void {
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
                            arrayItem as {
                                [key: string]: AliasedTileNodeValue;
                            },
                        );
                    }
                }
            } else if (value && typeof value === "object") {
                traverseObject(
                    value as unknown as { [key: string]: AliasedTileNodeValue },
                );
            }
        }
    }

    traverseObject(payload.aliased_data);
    return collectedEntries;
}
