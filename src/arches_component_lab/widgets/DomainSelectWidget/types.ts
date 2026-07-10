import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type {
    DomainAliasedNodeData,
    DomainCardXNodeXWidgetData,
} from "@/arches_component_lab/datatypes/domain/types.ts";

export interface DomainSelectWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: DomainCardXNodeXWidgetData;
    aliasedNodeData?: DomainAliasedNodeData | null;
    value?: string | null;
}
