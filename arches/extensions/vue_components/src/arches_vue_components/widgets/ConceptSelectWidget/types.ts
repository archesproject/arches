import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { ConceptAliasedNodeData } from "@/arches_vue_components/datatypes/concept/types.ts";

export interface ConceptSelectWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: ConceptAliasedNodeData | null;
    value?: string | null;
}
