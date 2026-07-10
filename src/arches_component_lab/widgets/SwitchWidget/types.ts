import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type { BooleanCardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { BooleanAliasedNodeData } from "@/arches_component_lab/datatypes/boolean/types.ts";

export interface SwitchWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: BooleanCardXNodeXWidgetData;
    aliasedNodeData?: BooleanAliasedNodeData | null;
    value?: boolean | null;
}
