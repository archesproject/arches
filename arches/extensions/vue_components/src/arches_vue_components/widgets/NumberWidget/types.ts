import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type {
    NumberAliasedNodeData,
    NumberCardXNodeXWidgetData,
} from "@/arches_vue_components/datatypes/number/types.ts";

export interface NumberWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: NumberCardXNodeXWidgetData;
    aliasedNodeData?: NumberAliasedNodeData | null;
    value?: number | null;
}
