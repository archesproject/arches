import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { ResourceInstanceListAliasedNodeData } from "@/arches_component_lab/datatypes/resource-instance-list/types.ts";
import type { ResourceInstanceReference } from "@/arches_component_lab/datatypes/resource-instance/types";

export interface ResourceInstanceMultiselectWidgetProps
    extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: ResourceInstanceListAliasedNodeData | null;
    value?: ResourceInstanceReference[] | null;
}
