<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useGettext } from "vue3-gettext";

import { Form } from "@primevue/forms";

import Button from "primevue/button";
import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import GenericWidget from "@/arches_component_lab/generic/GenericWidget/GenericWidget.vue";

import { upsertTile } from "@/arches_component_lab/cards/api.ts";
import { EDIT } from "@/arches_component_lab/widgets/constants.ts";

import type { FormSubmitEvent } from "@primevue/forms";
import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { AliasedTileData } from "@/arches_component_lab/cards/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types";

const { $gettext } = useGettext();

const { cardXNodeXWidgetData, graphSlug, mode, nodegroupAlias, tileData } =
    defineProps<{
        cardXNodeXWidgetData: CardXNodeXWidget[];
        graphSlug: string;
        mode: WidgetMode;
        nodegroupAlias: string;
        tileData: AliasedTileData | undefined;
    }>();

const emit = defineEmits(["update:isDirty", "update:tileData"]);

const formKey = ref(0);
const isSaving = ref(false);
const saveError = ref<Error | undefined>(undefined);

const aliasedData = reactive({ ...tileData?.aliased_data });

const widgetDirtyStates = reactive(
    cardXNodeXWidgetData.reduce<Record<string, boolean>>(
        (dirtyStatesMap, widgetData) => {
            dirtyStatesMap[widgetData.node.alias] = false;
            return dirtyStatesMap;
        },
        {},
    ),
);

const isDirty = computed(() => {
    return Object.values(widgetDirtyStates).some(
        (widgetDirtyState) => widgetDirtyState,
    );
});

watch(isDirty, (newValue, oldValue) => {
    if (newValue !== oldValue) {
        emit("update:isDirty", newValue);
    }
});

function resetForm() {
    Object.assign(aliasedData, tileData?.aliased_data);

    Object.keys(widgetDirtyStates).forEach((key) => {
        widgetDirtyStates[key] = false;
    });

    formKey.value += 1;
}

async function save(_event: FormSubmitEvent) {
    isSaving.value = true;

    try {
        const updatedTileData = {
            ...tileData,
            aliased_data: {
                ...tileData?.aliased_data,
                ...aliasedData,
            },
        } as AliasedTileData;

        const upsertedTileData = await upsertTile(
            graphSlug,
            nodegroupAlias,
            updatedTileData,
            tileData?.tileid,
        );

        Object.assign(aliasedData, upsertedTileData.aliased_data);

        emit("update:tileData", upsertedTileData);
        emit("update:isDirty", false);
    } catch (error) {
        saveError.value = error as Error;
    } finally {
        isSaving.value = false;
    }
}
</script>

<template>
    <Skeleton
        v-if="isSaving"
        style="height: 10rem"
    />
    <template v-else>
        <Message
            v-if="saveError"
            severity="error"
        >
            {{ saveError.message }}
        </Message>
        <Form
            :key="formKey"
            class="form"
            @submit="save"
        >
            <template
                v-for="cardXNodeXWidgetDatum in cardXNodeXWidgetData"
                :key="cardXNodeXWidgetDatum.id"
            >
                <GenericWidget
                    v-if="cardXNodeXWidgetDatum.visible"
                    v-model:value="
                        aliasedData[cardXNodeXWidgetDatum.node.alias]
                    "
                    v-model:is-dirty="
                        widgetDirtyStates[cardXNodeXWidgetDatum.node.alias]
                    "
                    :mode="mode"
                    :graph-slug="graphSlug"
                    :node-alias="cardXNodeXWidgetDatum.node.alias"
                    :card-x-node-x-widget-data="cardXNodeXWidgetDatum"
                />
            </template>

            <div style="display: flex">
                <Button
                    type="submit"
                    :disabled="isSaving"
                    :label="$gettext('Save')"
                />

                <Button
                    v-if="mode === EDIT"
                    type="button"
                    :label="$gettext('Cancel')"
                    @click="resetForm"
                />
            </div>
        </Form>
    </template>
</template>

<style scoped>
.form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
</style>
