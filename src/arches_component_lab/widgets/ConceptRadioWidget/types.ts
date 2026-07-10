import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type { ConceptCardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { ConceptAliasedNodeData } from "@/arches_component_lab/datatypes/concept/types.ts";

export interface ConceptRadioWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: ConceptCardXNodeXWidgetData;
    aliasedNodeData?: ConceptAliasedNodeData | null;
    value?: string | null;
}
