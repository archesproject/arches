import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { NodeValueAliasedNodeData } from "@/arches_vue_components/datatypes/node-value/types.ts";

export interface NodeValueSelectWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: NodeValueAliasedNodeData | null;
    value?: string | null;
}
