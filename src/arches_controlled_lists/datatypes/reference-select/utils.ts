import { getItemLabel } from "@/arches_controlled_lists/utils.ts";

import type {
    ReferenceSelectAliasedNodeData,
    ReferenceSelectNodeValue,
} from "@/arches_controlled_lists/datatypes/reference-select/types.ts";

export function buildReferenceSelectAliasedNodeData(
    nodeValue: ReferenceSelectNodeValue[] | null,
    preferredLanguageCode: string,
    systemLanguageCode: string,
): ReferenceSelectAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value:
            nodeValue
                ?.map(
                    (item) =>
                        getItemLabel(
                            item,
                            preferredLanguageCode,
                            systemLanguageCode,
                        ).value,
                )
                .filter(Boolean)
                .join(", ") ?? "",
        details: nodeValue ?? [],
    };
}
