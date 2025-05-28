<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from "vue";
import { useGettext } from "vue3-gettext";

import { Form } from "@primevue/forms";

import Button from "primevue/button";
import ProgressSpinner from "primevue/progressspinner";

import { upsertTile } from "@/arches_component_lab/cards/api.ts";

import { EDIT } from "@/arches_component_lab/widgets/constants.ts";

import type { FormSubmitEvent } from "@primevue/forms";
import type { useFormFieldState } from "@primevue/forms/useform";

import type { WidgetConfiguration } from "@/arches_component_lab/cards/types.ts";
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
    widgets: WidgetConfiguration[];
}>();

const emit = defineEmits(["update:isDirty", "update:tileData"]);

const { $gettext } = useGettext();

const formKey = ref(0);
const formRef = useTemplateRef("form");

const isSaving = ref(false);

const isDirty = computed(() => {
    // @ts-expect-error This is a bug with PrimeVue types
    const states = formRef.value?.states;

    if (!states) {
        return false;
    }

    return Object.values(states).some((state) => {
        return (state as useFormFieldState).dirty;
    });
});

watch(isDirty, (newValue, oldValue) => {
    if (newValue !== oldValue) {
        emit("update:isDirty", newValue);
    }
});

async function save(e: FormSubmitEvent) {
    isSaving.value = true;

    try {
        const updatedTileData = {
            ...props.tileData,
            aliased_data: {
                ...props.tileData.aliased_data,
                ...e.values,
            },
        };

        const foo = await upsertTile(
            props.graphSlug,
            props.nodegroupGroupingNodeAlias,
            updatedTileData,
            props.tileData.tileid,
        );

        console.log("Updated tile data:", foo);
        emit("update:tileData", updatedTileData); // or foo?
    } catch (error) {
        console.error("Failed to save tile data:", error);
        // toast.add({
        //     severity: ERROR,
        //     life: DEFAULT_ERROR_TOAST_LIFE,
        //     summary: $gettext("Failed to save data."),
        //     detail: error instanceof Error ? error.message : undefined,
        // });
    } finally {
        isSaving.value = false;
    }
}
</script>

<template>
    <ProgressSpinner v-if="isSaving" />
    <Form
        v-else
        ref="form"
        :key="formKey"
        @submit="save"
    >
        <component
            :is="widget.component"
            v-for="widget in widgets"
            :key="widget.cardXNodeXWidgetDatum.id"
            :mode="props.mode"
            :graph-slug="props.graphSlug"
            :node-alias="widget.cardXNodeXWidgetDatum.node.alias"
            :card-x-node-x-widget-data="widget.cardXNodeXWidgetDatum"
            :initial-value="
                tileData.aliased_data[widget.cardXNodeXWidgetDatum.node.alias]
            "
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
                @click="formKey++"
            />
        </div>
    </Form>
</template>
