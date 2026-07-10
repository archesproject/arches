import type { BaseWidgetProps } from "@/arches_component_lab/widgets/types.ts";
import type {
    DomainCardXNodeXWidgetData,
    DomainListAliasedNodeData,
} from "@/arches_component_lab/datatypes/domain/types.ts";

export interface DomainCheckboxWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: DomainCardXNodeXWidgetData;
    aliasedNodeData?: DomainListAliasedNodeData | null;
    value?: string[] | null;
}
