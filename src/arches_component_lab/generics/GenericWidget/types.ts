import type {
    AliasedNodeData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

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
