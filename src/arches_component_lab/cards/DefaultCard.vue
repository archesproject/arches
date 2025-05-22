<script setup lang="ts">
import { computed, defineAsyncComponent, ref, watchEffect } from "vue";

import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";

import {
    fetchCardData,
    fetchTileData,
} from "@/arches_component_lab/cards/api.ts";
import { fetchWidgetDataFromCard } from "@/arches_component_lab/widgets/api.ts";

import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

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

const isLoading = ref();
const configurationError = ref();

const cardData = ref();
const cardXNodeXWidgetData = ref();
const tileData = ref();

interface WidgetEntry {
    component: ReturnType<typeof defineAsyncComponent>;
    cardXNodeXWidgetDatum: CardXNodeXWidgetDatum;
}

interface CardXNodeXWidgetDatum {
    card: {
        name: string;
    };
    id: string;
    node: {
        alias: string;
    };
    widget: {
        component: string;
    };
}

const widgets = computed(() => {
    return cardXNodeXWidgetData.value.reduce(
        (acc: WidgetEntry[], cardXNodeXWidgetDatum: CardXNodeXWidgetDatum) => {
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
            <component
                :is="widget.component"
                v-for="widget in widgets"
                :key="widget.cardXNodeXWidgetDatum.id"
                :mode="props.mode"
                :graph-slug="props.graphSlug"
                :node-alias="widget.cardXNodeXWidgetDatum.node.alias"
                :card-x-node-x-widget-data="widget.cardXNodeXWidgetDatum"
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
