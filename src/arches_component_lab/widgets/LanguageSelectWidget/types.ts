import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { LanguageAliasedNodeData } from "@/arches_component_lab/datatypes/language/types.ts";

export interface LanguageSelectWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: LanguageAliasedNodeData | null;
    value?: string | null;
}
