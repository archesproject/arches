<script setup lang="ts">
import GenericWidget from "@/arches_component_lab/generics/GenericWidget/GenericWidget.vue";
import { isAliasedNodeData } from "@/arches_component_lab/generics/GenericCard/utils.ts";
import { VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type {
    AliasedNodeData,
    AliasedTileData,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";

const { cardXNodeXWidgetData, graphSlug, tileData } = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidgetData[];
    graphSlug: string;
    nodegroupAlias: string;
    tileData?: AliasedTileData;
}>();

const emit = defineEmits<{
    initialized: [aliasedNodeData: Record<string, AliasedNodeData>];
}>();

const initializedNodeAliases = new Set<string>();
const initializedNodeData: Record<string, AliasedNodeData> = {};

function onWidgetInitialized(
    nodeAlias: string,
    aliasedNodeData: AliasedNodeData,
) {
    initializedNodeData[nodeAlias] = aliasedNodeData;
    initializedNodeAliases.add(nodeAlias);

    const allVisibleWidgetsInitialized = cardXNodeXWidgetData
        .filter((datum) => datum.visible)
        .every((datum) => initializedNodeAliases.has(datum.node.alias));

    if (allVisibleWidgetsInitialized) {
        emit("initialized", initializedNodeData);
    }
}

function getAliasedNodeData(nodeAlias: string): AliasedNodeData | null {
    const entry = tileData?.aliased_data?.[nodeAlias];
    return isAliasedNodeData(entry) ? entry : null;
}
</script>

<template>
    <div class="viewer">
        <template
            v-for="cardXNodeXWidgetDatum in cardXNodeXWidgetData"
            :key="cardXNodeXWidgetDatum.id"
        >
            <GenericWidget
                v-if="cardXNodeXWidgetDatum.visible"
                :aliased-node-data="
                    getAliasedNodeData(cardXNodeXWidgetDatum.node.alias)
                "
                :card-x-node-x-widget-data="cardXNodeXWidgetDatum"
                :graph-slug="graphSlug"
                :mode="VIEW"
                :node-alias="cardXNodeXWidgetDatum.node.alias"
                @initialized="
                    onWidgetInitialized(
                        cardXNodeXWidgetDatum.node.alias,
                        $event,
                    )
                "
            />
        </template>
    </div>
</template>

<style scoped>
.viewer {
    display: flex;
    flex-direction: column;
    gap: 1.4rem;
}
</style>
