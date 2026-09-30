import type { BaseWidgetProps } from "@/arches_vue_components/widgets/types.ts";
import type { CardXNodeXWidgetData } from "@/arches_vue_components/types.ts";
import type {
    URLAliasedNodeData,
    URLNodeValue,
} from "@/arches_vue_components/datatypes/url/types.ts";

export interface URLWidgetProps extends BaseWidgetProps {
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    aliasedNodeData?: URLAliasedNodeData | null;
    value?: URLNodeValue | null;
}
