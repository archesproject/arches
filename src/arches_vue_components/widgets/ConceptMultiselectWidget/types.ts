import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { ConceptListAliasedNodeData } from "@/arches_vue_components/datatypes/concept-list/types.ts";

export interface ConceptMultiselectWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: ConceptListAliasedNodeData | null;
    value?: string[] | null;
}
