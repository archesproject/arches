import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type {
    ResourceInstanceAliasedNodeData,
    ResourceInstanceReference,
} from "@/arches_component_lab/datatypes/resource-instance/types";

export interface ResourceInstanceSelectWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: ResourceInstanceAliasedNodeData | null;
    value?: ResourceInstanceReference | null;
    defaultTerm?: string;
}
