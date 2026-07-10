import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type {
    DateAliasedNodeData,
    DateCardXNodeXWidgetData,
} from "@/arches_component_lab/datatypes/date/types.ts";

export interface DatePickerWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: DateCardXNodeXWidgetData;
    aliasedNodeData?: DateAliasedNodeData | null;
    value?: string | null;
}
