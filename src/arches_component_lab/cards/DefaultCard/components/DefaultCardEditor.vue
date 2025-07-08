<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useGettext } from "vue3-gettext";

import { Form } from "@primevue/forms";

import Button from "primevue/button";
import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import GenericWidget from "@/arches_component_lab/widgets/GenericWidget/GenericWidget.vue";

import { upsertTile } from "@/arches_component_lab/cards/api.ts";
import { EDIT } from "@/arches_component_lab/widgets/constants.ts";

import type { FormSubmitEvent } from "@primevue/forms";
import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types";

const props = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidget[];
    graphSlug: string;
    mode: WidgetMode;
    nodegroupAlias: string;
    tileData: {
        tileid: string;
        aliased_data: {
            [key: string]: {
                display_value: string;
                interchange_value: unknown;
            };
        };
    };
}>();

const emit = defineEmits(["update:isDirty", "update:tileData"]);

const { $gettext } = useGettext();

const formKey = ref(0);

const isSaving = ref(false);
const saveError = ref();

const localData = reactive({ ...props.tileData.aliased_data });

const widgetDirtyStates = reactive(
    props.cardXNodeXWidgetData.reduce(
        (acc, widget) => {
            acc[widget.node.alias] = false;
            return acc;
        },
        {} as Record<string, boolean>,
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
    Object.assign(localData, props.tileData.aliased_data);

    Object.keys(widgetDirtyStates).forEach((key) => {
        widgetDirtyStates[key] = false;
    });

    formKey.value += 1;
}

async function save(_event: FormSubmitEvent) {
    isSaving.value = true;

    try {
        const updatedTileData = {
            ...props.tileData,
            aliased_data: {
                ...props.tileData.aliased_data,
                ...localData,
            },
        };

        const upsertedTileData = await upsertTile(
            props.graphSlug,
            props.nodegroupAlias,
            updatedTileData,
            props.tileData.tileid,
        );

        Object.assign(localData, updatedTileData.aliased_data);

        emit("update:tileData", upsertedTileData);
    } catch (error) {
        saveError.value = error;
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
                        localData[cardXNodeXWidgetDatum.node.alias]
                            .interchange_value
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
