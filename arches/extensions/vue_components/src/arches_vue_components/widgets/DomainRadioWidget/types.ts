import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type {
    DomainAliasedNodeData,
    DomainCardXNodeXWidgetData,
} from "@/arches_vue_components/datatypes/domain/types.ts";

export interface DomainRadioWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: DomainCardXNodeXWidgetData;
    aliasedNodeData?: DomainAliasedNodeData | null;
    value?: string | null;
}
