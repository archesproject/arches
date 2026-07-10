import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type { StringCardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type {
    LanguageValue,
    StringAliasedNodeData,
} from "@/arches_component_lab/datatypes/string/types.ts";

export interface TextWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: StringCardXNodeXWidgetData;
    aliasedNodeData?: StringAliasedNodeData | null;
    value?: Record<string, LanguageValue> | null;
    renderContext?: string;
}
