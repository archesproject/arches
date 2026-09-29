import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { ConceptCardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { ConceptListAliasedNodeData } from "@/arches_vue_components/datatypes/concept-list/types.ts";

export interface ConceptCheckboxWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: ConceptCardXNodeXWidgetData;
    aliasedNodeData?: ConceptListAliasedNodeData | null;
    value?: string[] | null;
}
