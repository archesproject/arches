import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";

import type {
    ReferenceSelectAliasedNodeData,
    ReferenceSelectDatatypeCardXNodeXWidgetData,
    ReferenceSelectNodeValue,
} from "@/arches_controlled_lists/datatypes/reference-select/types.ts";

export interface ReferenceSelectWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: ReferenceSelectDatatypeCardXNodeXWidgetData;
    aliasedNodeData?: ReferenceSelectAliasedNodeData | null;
    value?: ReferenceSelectNodeValue[] | null;
}
