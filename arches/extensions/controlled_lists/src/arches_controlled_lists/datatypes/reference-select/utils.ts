import { getItemLabel } from "@/arches_controlled_lists/utils.ts";

import type {
    ReferenceSelectAliasedNodeData,
    ReferenceSelectNodeValue,
    ReferenceSelectDetails,
} from "@/arches_controlled_lists/datatypes/reference-select/types.ts";

export function buildReferenceSelectAliasedNodeData(
    nodeValue: ReferenceSelectNodeValue[] | null,
    preferredLanguageCode: string,
    systemLanguageCode: string,
): ReferenceSelectAliasedNodeData {
    const details: ReferenceSelectDetails[] = nodeValue
        ? nodeValue.map((item) => ({
              children: [],
              display_value: getItemLabel(
                  item,
                  preferredLanguageCode,
                  systemLanguageCode,
              ).value,
              list_item_id: item.labels[0]?.list_item_id ?? "",
              list_item_values: item.labels,
              sortorder: 0,
              uri: item.uri,
          }))
        : [];
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
        details: details,
    };
}
