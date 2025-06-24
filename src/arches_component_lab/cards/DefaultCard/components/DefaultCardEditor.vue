<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useGettext } from "vue3-gettext";

import { Form } from "@primevue/forms";

import Button from "primevue/button";
import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import { upsertTile } from "@/arches_component_lab/cards/api.ts";

import { EDIT } from "@/arches_component_lab/widgets/constants.ts";

import type { FormSubmitEvent } from "@primevue/forms";

import type { WidgetComponent } from "@/arches_component_lab/cards/types.ts";
import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";

const props = defineProps<{
    cardXNodeXWidgetData: CardXNodeXWidget[];
    graphSlug: string;
    mode: string;
    nodegroupGroupingNodeAlias: string;
    tileData: {
        tileid: string;
        aliased_data: Record<string, unknown>;
    };
    widgets: WidgetComponent[];
}>();

const emit = defineEmits(["update:isDirty", "update:tileData"]);

const { $gettext } = useGettext();

const formKey = ref(0);

const isSaving = ref(false);
const saveError = ref();

const localData = reactive({ ...props.tileData.aliased_data });

const widgetDirtyStates = reactive(
    props.widgets.reduce(
        (acc, widget) => {
            acc[widget.cardXNodeXWidgetData.node.alias] = false;
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
            props.nodegroupGroupingNodeAlias,
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
            <component
                :is="widget.component"
                v-for="widget in widgets"
                :key="widget.cardXNodeXWidgetData.id"
                v-model:value="
                    localData[widget.cardXNodeXWidgetData.node.alias]
                "
                v-model:is-dirty="
                    widgetDirtyStates[widget.cardXNodeXWidgetData.node.alias]
                "
                :mode="props.mode"
                :graph-slug="props.graphSlug"
                :node-alias="widget.cardXNodeXWidgetData.node.alias"
                :card-x-node-x-widget-data="widget.cardXNodeXWidgetData"
            />

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
