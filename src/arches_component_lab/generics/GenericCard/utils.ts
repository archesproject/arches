import type { AliasedData } from "@/arches_component_lab/types.ts";

export function extractFileEntriesFromAliasedData(
    payload: AliasedData,
): { file: File; nodeId: string }[] {
    const collectedEntries: { file: File; nodeId: string }[] = [];

    function traverseObject(currentObject: AliasedData): void {
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
                        traverseObject(arrayItem as unknown as AliasedData);
                    }
                }
            } else if (value && typeof value === "object") {
                traverseObject(value as unknown as AliasedData);
            }
        }
    }

    traverseObject(payload);
    return collectedEntries;
}
