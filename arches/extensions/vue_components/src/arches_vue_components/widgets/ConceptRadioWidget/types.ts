import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { ConceptCardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { ConceptAliasedNodeData } from "@/arches_vue_components/datatypes/concept/types.ts";

export interface ConceptRadioWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: ConceptCardXNodeXWidgetData;
    aliasedNodeData?: ConceptAliasedNodeData | null;
    value?: string | null;
}
