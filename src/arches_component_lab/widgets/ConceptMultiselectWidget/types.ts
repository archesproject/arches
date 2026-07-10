import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { ConceptListAliasedNodeData } from "@/arches_component_lab/datatypes/concept-list/types.ts";

export interface ConceptMultiselectWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: ConceptListAliasedNodeData | null;
    value?: string[] | null;
}
