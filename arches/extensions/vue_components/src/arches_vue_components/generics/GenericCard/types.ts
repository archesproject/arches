import type { AliasedTileData } from "@/arches_vue_components/types.ts";
import type { WidgetMode } from "@/arches_vue_components/widgets/types.ts";

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
