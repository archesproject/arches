export function extractFileEntriesFromPayload(
    payloadObject: Record<string, unknown>,
) {
    const fileEntries: { file: File; nodeId: string }[] = [];

    function recurse(currentObject: Record<string, unknown>): void {
        for (const key in currentObject) {
            if (!Object.prototype.hasOwnProperty.call(currentObject, key)) {
                continue;
            }
            const value = currentObject[key];
            if (value instanceof File) {
                const possibleNodeId = currentObject["node_id"];
                if (typeof possibleNodeId === "string") {
                    fileEntries.push({
                        file: value,
                        nodeId: possibleNodeId,
                    });
                }
                delete currentObject[key];
            } else if (value && typeof value === "object") {
                if (Array.isArray(value)) {
                    for (const item of value) {
                        if (item && typeof item === "object") {
                            recurse(item as Record<string, unknown>);
                        }
                    }
                } else {
                    recurse(value as Record<string, unknown>);
                }
            }
        }
    }

    recurse(payloadObject);
    return fileEntries;
}
