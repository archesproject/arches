import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { EDTFAliasedNodeData } from "@/arches_component_lab/datatypes/edtf/types.ts";

export interface EDTFWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: EDTFAliasedNodeData | null;
    value?: string | null;
}
