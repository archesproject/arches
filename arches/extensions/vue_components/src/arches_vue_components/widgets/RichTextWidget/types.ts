import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { StringCardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type {
    LanguageValue,
    StringAliasedNodeData,
} from "@/arches_vue_components/datatypes/string/types.ts";

export interface RichTextWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: StringCardXNodeXWidgetData;
    aliasedNodeData?: StringAliasedNodeData | null;
    value?: Record<string, LanguageValue> | null;
}
