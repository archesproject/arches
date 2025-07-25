<script setup lang="ts">
import { reactive, toRaw, ref, watch, nextTick } from "vue";
import { useGettext } from "vue3-gettext";

import { Form } from "@primevue/forms";
import Button from "primevue/button";
import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import GenericWidget from "@/arches_component_lab/generics/GenericWidget/GenericWidget.vue";

import { upsertTile } from "@/arches_component_lab/generics/GenericCard/api.ts";
import { EDIT } from "@/arches_component_lab/widgets/constants.ts";

import type {
    AliasedTileNodeValue,
    CardXNodeXWidgetData,
} from "@/arches_component_lab/types.ts";
import type { AliasedTileData } from "@/arches_component_lab/generics/GenericCard/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const { $gettext } = useGettext();

const props = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidgetData[];
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

const originalAliasedData = structuredClone(props.tileData?.aliased_data || {});
const aliasedData = reactive(
    structuredClone(props.tileData?.aliased_data || {}),
);

const widgetDirtyStates = reactive(
    props.cardXNodeXWidgetData.reduce<Record<string, boolean>>(
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
            ...props.tileData,
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

function onUpdateWidgetValue(nodeAlias: string, value: AliasedTileNodeValue) {
    aliasedData[nodeAlias] = value;
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
            props.graphSlug,
            props.nodegroupAlias,
            {
                ...(props.tileData as AliasedTileData),
                aliased_data: toRaw(aliasedData),
            },
            props.tileData?.tileid,
            props.resourceInstanceId,
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

        // nextTick ensures `save` is emitted after `update:tileData`
        nextTick(() => {
            emit("save", updatedTileData);
        });
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
                    :disabled="isSaving"
                    :label="$gettext('Save')"
                    @click="save"
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
