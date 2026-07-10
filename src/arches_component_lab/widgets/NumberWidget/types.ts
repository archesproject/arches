import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type {
    NumberAliasedNodeData,
    NumberCardXNodeXWidgetData,
} from "@/arches_component_lab/datatypes/number/types.ts";

export interface NumberWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: NumberCardXNodeXWidgetData;
    aliasedNodeData?: NumberAliasedNodeData | null;
    value?: number | null;
}
