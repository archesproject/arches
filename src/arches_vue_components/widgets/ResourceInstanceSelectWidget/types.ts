import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type {
    ResourceInstanceAliasedNodeData,
    ResourceInstanceReference,
} from "@/arches_vue_components/datatypes/resource-instance/types";

export interface ResourceInstanceSelectWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: ResourceInstanceAliasedNodeData | null;
    value?: ResourceInstanceReference | null;
    defaultTerm?: string;
}
