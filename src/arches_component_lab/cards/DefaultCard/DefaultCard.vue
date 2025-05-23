<script setup lang="ts">
import { computed, defineAsyncComponent, ref, watchEffect } from "vue";

import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";

import DefaultCardEditor from "@/arches_component_lab/cards/DefaultCard/components/DefaultCardEditor.vue";
import DefaultCardViewer from "@/arches_component_lab/cards/DefaultCard/components/DefaultCardViewer.vue";

import {
    fetchCardData,
    fetchTileData,
} from "@/arches_component_lab/cards/api.ts";
import { fetchWidgetDataFromCard } from "@/arches_component_lab/widgets/api.ts";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";
import type {
    CardXNodeXWidgetDatum,
    WidgetConfiguration,
} from "@/arches_component_lab/cards/types.ts";

// TODO: Remove this when 7.6 stops being supported
const deprecatedComponentPathToUpdatedComponentPath: Record<string, string> = {
    "views/components/widgets/text":
        "arches_component_lab/widgets/NonLocalizedStringWidget/NonLocalizedStringWidget",
};

const props = defineProps<{
    mode: WidgetMode;
    nodegroupGroupingNodeAlias: string;
    graphSlug: string;
    tileId?: string;
}>();

const emit = defineEmits(["update:isDirty", "update:tileData"]);

const isLoading = ref();
const configurationError = ref();

const cardData = ref();
const cardXNodeXWidgetData = ref();
const tileData = ref();

const widgets = computed(() => {
    return cardXNodeXWidgetData.value.reduce(
        (
            acc: WidgetConfiguration[],
            cardXNodeXWidgetDatum: CardXNodeXWidgetDatum,
        ) => {
            if (
                !deprecatedComponentPathToUpdatedComponentPath[
                    cardXNodeXWidgetDatum.widget.component
                ]
            ) {
                return acc;
            }

            const component = defineAsyncComponent(() => {
                return import(
                    `@/${deprecatedComponentPathToUpdatedComponentPath[cardXNodeXWidgetDatum.widget.component]}.vue`
                );
            });

            acc.push({
                component: component,
                cardXNodeXWidgetDatum: cardXNodeXWidgetDatum,
            });

            return acc;
        },
        [],
    );
});

watchEffect(async () => {
    isLoading.value = true;

    try {
        const cardPromise = fetchCardData(
            props.graphSlug,
            props.nodegroupGroupingNodeAlias,
        );
        const widgetPromise = fetchWidgetDataFromCard(
            props.graphSlug,
            props.nodegroupGroupingNodeAlias,
        );
        const tilePromise = fetchTileData(
            props.graphSlug,
            props.nodegroupGroupingNodeAlias,
            props.tileId,
        );

        cardData.value = await cardPromise;
        cardXNodeXWidgetData.value = await widgetPromise;
        tileData.value = await tilePromise;
    } catch (error) {
        configurationError.value = error;
    } finally {
        isLoading.value = false;
    }
});
</script>

<template>
    <div class="card">
        <ProgressSpinner v-if="isLoading" />
        <Message
            v-else-if="configurationError"
            severity="error"
        >
            {{ configurationError.message }}
        </Message>
        <template v-else>
            <label>
                <span>{{ cardData.name }}</span>
            </label>

            <DefaultCardEditor
                v-if="props.mode === EDIT"
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :graph-slug="props.graphSlug"
                :mode="props.mode"
                :nodegroup-grouping-node-alias="
                    props.nodegroupGroupingNodeAlias
                "
                :tile-data="tileData"
                :widgets="widgets"
                @update:is-dirty="emit('update:isDirty', $event)"
                @update:tile-data="emit('update:tileData', $event)"
            />
            <DefaultCardViewer
                v-else-if="props.mode === VIEW"
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :graph-slug="props.graphSlug"
                :mode="props.mode"
                :nodegroup-grouping-node-alias="
                    props.nodegroupGroupingNodeAlias
                "
                :tile-data="tileData"
                :widgets="widgets"
            />
        </template>
    </div>
</template>

<style scoped>
.card {
    display: flex;
    flex-direction: column;
    gap: 0.5em;
    width: 100%;
}
</style>
