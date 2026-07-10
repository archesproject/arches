import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { ConceptAliasedNodeData } from "@/arches_component_lab/datatypes/concept/types.ts";

export interface ConceptSelectWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: ConceptAliasedNodeData | null;
    value?: string | null;
}
