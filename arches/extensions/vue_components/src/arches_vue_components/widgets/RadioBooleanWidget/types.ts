import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { BooleanCardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { BooleanAliasedNodeData } from "@/arches_vue_components/datatypes/boolean/types.ts";

export interface RadioBooleanWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: BooleanCardXNodeXWidgetData;
    aliasedNodeData?: BooleanAliasedNodeData | null;
    value?: boolean | null;
}
