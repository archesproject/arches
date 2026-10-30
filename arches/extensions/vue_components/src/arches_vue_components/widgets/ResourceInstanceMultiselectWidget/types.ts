import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type { ResourceInstanceListAliasedNodeData } from "@/arches_vue_components/datatypes/resource-instance-list/types.ts";
import type { ResourceInstanceReference } from "@/arches_vue_components/datatypes/resource-instance/types";

export interface ResourceInstanceMultiselectWidgetProps
    extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: ResourceInstanceListAliasedNodeData | null;
    value?: ResourceInstanceReference[] | null;
}
