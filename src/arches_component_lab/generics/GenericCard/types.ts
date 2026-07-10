import type { AliasedTileData } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

export interface GenericCardProps {
    mode: WidgetMode;
    nodegroupAlias: string;
    graphSlug: string;
    resourceInstanceId?: string | null;
    selectedNodeAlias?: string | null;
    shouldShowFormButtons?: boolean;
    tileData?: AliasedTileData;
    tileId?: string | null;
}
