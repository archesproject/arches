import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type {
    DomainCardXNodeXWidgetData,
    DomainListAliasedNodeData,
} from "@/arches_vue_components/datatypes/domain/types.ts";

export interface DomainMultiselectWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: DomainCardXNodeXWidgetData;
    aliasedNodeData?: DomainListAliasedNodeData | null;
    value?: string[] | null;
}
