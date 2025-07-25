<script setup lang="ts">
import { ref, useTemplateRef, watchEffect } from "vue";
import { useGettext } from "vue3-gettext";

import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import GenericCardEditor from "@/arches_component_lab/generics/GenericCard/components/GenericCardEditor.vue";
import GenericCardViewer from "@/arches_component_lab/generics/GenericCard/components/GenericCardViewer.vue";

import {
    fetchTileData,
    fetchCardXNodeXWidgetDataFromNodeGroup,
} from "@/arches_component_lab/generics/GenericCard/api.ts";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { AliasedTileData } from "@/arches_component_lab/generics/GenericCard/types";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const { $gettext } = useGettext();

const props = withDefaults(
    defineProps<{
        mode: WidgetMode;
        nodegroupAlias: string;
        graphSlug: string;
        resourceInstanceId?: string | null;
        shouldShowFormButtons?: boolean;
        tileData?: AliasedTileData;
        tileId?: string | null;
    }>(),
    {
        shouldShowFormButtons: true,
        resourceInstanceId: undefined,
        tileData: undefined,
        tileId: undefined,
    },
);

const emit = defineEmits([
    "update:widgetDirtyStates",
    "update:tileData",
    "save",
]);

const isLoading = ref(true);
const configurationError = ref();
const cardXNodeXWidgetData = ref<CardXNodeXWidgetData[]>([]);
const aliasedTileData = ref<AliasedTileData>();

const defaultCardEditor = useTemplateRef("defaultCardEditor");

watchEffect(async () => {
    isLoading.value = true;

    try {
        const cardXNodeXWidgetDataPromise =
            fetchCardXNodeXWidgetDataFromNodeGroup(
                props.graphSlug,
                props.nodegroupAlias,
            );

        if (!props.tileData && !props.tileId && !props.resourceInstanceId) {
            throw new Error(
                $gettext(
                    "No tile data, tile ID, or resource instance ID provided.",
                ),
            );
        }

        if (props.tileData) {
            aliasedTileData.value = props.tileData;
        } else if (props.tileId) {
            const aliasedTileDataPromise = fetchTileData(
                props.graphSlug,
                props.nodegroupAlias,
                props.tileId,
            );
            aliasedTileData.value = await aliasedTileDataPromise;
        } else if (props.resourceInstanceId) {
            // TODO: Replace with querysets call for empty tile structure
            // @ts-expect-error this is an incomplete tile structure
            aliasedTileData.value = {
                resourceinstance: props.resourceInstanceId,
                aliased_data: {},
            };
        }

        cardXNodeXWidgetData.value = await cardXNodeXWidgetDataPromise;
    } catch (error) {
        configurationError.value = error;
    } finally {
        isLoading.value = false;
    }
});

defineExpose({
    save: function () {
        if (defaultCardEditor.value) {
            defaultCardEditor.value.save();
        }
    },
});
</script>

<template>
    <div class="card">
        <Skeleton
            v-if="isLoading"
            style="height: 10rem"
        />
        <Message
            v-else-if="configurationError"
            severity="error"
        >
            {{ configurationError.message }}
        </Message>
        <template v-else>
            <span>{{ cardXNodeXWidgetData[0].card.name }}</span>

            <GenericCardEditor
                v-if="mode === EDIT"
                ref="defaultCardEditor"
                v-model:tile-data="aliasedTileData"
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :graph-slug="graphSlug"
                :mode="mode"
                :nodegroup-alias="nodegroupAlias"
                :resource-instance-id="resourceInstanceId"
                :should-show-form-buttons="shouldShowFormButtons"
                @save="emit('save', $event)"
                @update:widget-dirty-states="
                    emit('update:widgetDirtyStates', $event)
                "
                @update:tile-data="emit('update:tileData', $event)"
            />
            <GenericCardViewer
                v-else-if="mode === VIEW"
                v-model:tile-data="aliasedTileData"
                :card-x-node-x-widget-data="cardXNodeXWidgetData"
                :graph-slug="graphSlug"
                :mode="mode"
                :nodegroup-alias="nodegroupAlias"
            />
        </template>
    </div>
</template>

<style scoped>
.card {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
}
</style>
