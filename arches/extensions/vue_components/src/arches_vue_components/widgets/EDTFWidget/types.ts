import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { EDTFAliasedNodeData } from "@/arches_vue_components/datatypes/edtf/types.ts";

export interface EDTFWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: EDTFAliasedNodeData | null;
    value?: string | null;
}
