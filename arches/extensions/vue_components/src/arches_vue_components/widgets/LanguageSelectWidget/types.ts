import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { LanguageAliasedNodeData } from "@/arches_vue_components/datatypes/language/types.ts";

export interface LanguageSelectWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: LanguageAliasedNodeData | null;
    value?: string | null;
}
