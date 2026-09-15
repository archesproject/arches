import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type {
    DateAliasedNodeData,
    DateCardXNodeXWidgetData,
} from "@/arches_vue_components/datatypes/date/types.ts";

export interface DatePickerWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: DateCardXNodeXWidgetData;
    aliasedNodeData?: DateAliasedNodeData | null;
    value?: string | null;
}
