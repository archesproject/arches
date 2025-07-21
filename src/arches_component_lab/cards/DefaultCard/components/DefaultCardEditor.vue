<script setup lang="ts">
import { reactive, toRaw, ref, watch } from "vue";
import { useGettext } from "vue3-gettext";

import { Form } from "@primevue/forms";
import Button from "primevue/button";
import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import GenericWidget from "@/arches_component_lab/generic/GenericWidget/GenericWidget.vue";

import { upsertTile } from "@/arches_component_lab/cards/api.ts";
import { EDIT } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { AliasedTileData } from "@/arches_component_lab/cards/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types";

const { $gettext } = useGettext();

const {
    cardXNodeXWidgetData,
    graphSlug,
    mode,
    nodegroupAlias,
    resourceInstanceId,
    shouldShowFormButtons = true,
    tileData,
} = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidget[];
    graphSlug: string;
    mode: WidgetMode;
    nodegroupAlias: string;
    resourceInstanceId: string | null | undefined;
    shouldShowFormButtons: boolean | undefined;
    tileData?: AliasedTileData;
}>();

const emit = defineEmits([
    "update:widgetDirtyStates",
    "update:tileData",
    "save",
]);

const formKey = ref(0);
const isSaving = ref(false);
const saveError = ref<Error>();

const originalAliasedData = structuredClone(tileData?.aliased_data || {});
const aliasedData = reactive(structuredClone(tileData?.aliased_data || {}));

const widgetDirtyStates = reactive(
    cardXNodeXWidgetData.reduce<Record<string, boolean>>(
        (dirtyStatesMap, widgetDatum) => {
            dirtyStatesMap[widgetDatum.node.alias] = false;
            return dirtyStatesMap;
        },
        {},
    ),
);

watch(
    aliasedData,
    () => {
        emit("update:tileData", {
            ...tileData,
            aliased_data: toRaw(aliasedData),
        });
    },
    { deep: true },
);

watch(
    widgetDirtyStates,
    (newValue) => {
        emit("update:widgetDirtyStates", newValue);
    },
    { deep: true },
);

// TODO: should we force widgets to coerce their values to match aliased data?
function onUpdateWidgetValue(nodeAlias: string, value: unknown) {
    aliasedData[nodeAlias].node_value = value;
}

function resetWidgetDirtyStates() {
    Object.keys(widgetDirtyStates).forEach((nodeAlias) => {
        widgetDirtyStates[nodeAlias] = false;
    });
}

function resetForm() {
    resetWidgetDirtyStates();

    Object.assign(aliasedData, structuredClone(originalAliasedData));
    formKey.value += 1;
}

async function save() {
    isSaving.value = true;
    saveError.value = undefined;

    try {
        const updatedTileData = await upsertTile(
            graphSlug,
            nodegroupAlias,
            {
                ...(tileData as AliasedTileData),
                aliased_data: toRaw(aliasedData),
            },
            tileData?.tileid,
            resourceInstanceId,
        );

        Object.assign(
            aliasedData,
            structuredClone(updatedTileData.aliased_data),
        );
        Object.assign(
            originalAliasedData,
            structuredClone(updatedTileData.aliased_data),
        );

        resetWidgetDirtyStates();

        emit("save", updatedTileData);
    } catch (error) {
        saveError.value = error as Error;
    } finally {
        isSaving.value = false;
    }
}

defineExpose({ save });
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
                    v-model:is-dirty="
                        widgetDirtyStates[cardXNodeXWidgetDatum.node.alias]
                    "
                    :mode="mode"
                    :graph-slug="graphSlug"
                    :node-alias="cardXNodeXWidgetDatum.node.alias"
                    :card-x-node-x-widget-data="cardXNodeXWidgetDatum"
                    :value="aliasedData[cardXNodeXWidgetDatum.node.alias]"
                    @update:value="
                        onUpdateWidgetValue(
                            cardXNodeXWidgetDatum.node.alias,
                            $event,
                        )
                    "
                />
            </template>

            <div
                v-if="shouldShowFormButtons"
                style="display: flex"
            >
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
