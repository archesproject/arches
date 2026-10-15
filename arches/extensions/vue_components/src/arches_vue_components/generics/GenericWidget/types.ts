import type {
    AliasedNodeData,
    CardXNodeXWidgetData,
} from "@/arches_vue_components/types.ts";
import type { WidgetMode } from "@/arches_vue_components/widgets/types.ts";

export interface GenericWidgetProps {
    aliasedNodeData?: AliasedNodeData | null | undefined;
    cardXNodeXWidgetData?: CardXNodeXWidgetData;
    cardXNodeXWidgetDataOverrides?: Partial<CardXNodeXWidgetData>;
    graphSlug: string;
    isDirty?: boolean;
    mode: WidgetMode;
    nodeAlias: string;
    shouldShowLabel?: boolean;
    value?: unknown | null | undefined;
}
