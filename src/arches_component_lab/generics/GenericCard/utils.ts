import type {
    AliasedData,
    AliasedNodeData,
} from "@/arches_component_lab/types.ts";

export function deepClone<T>(sourceObject: T): T {
    return JSON.parse(JSON.stringify(sourceObject));
}

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
