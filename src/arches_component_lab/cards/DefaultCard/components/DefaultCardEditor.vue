<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from "vue";
import { useGettext } from "vue3-gettext";

import { Form } from "@primevue/forms";

import Button from "primevue/button";
import Message from "primevue/message";
import Skeleton from "primevue/skeleton";

import { upsertTile } from "@/arches_component_lab/cards/api.ts";

import { EDIT } from "@/arches_component_lab/widgets/constants.ts";

import type { FormSubmitEvent } from "@primevue/forms";
import type { useFormFieldState } from "@primevue/forms/useform";

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
const formRef = useTemplateRef("form");

const isSaving = ref(false);
const saveError = ref();

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

        const upsertedTileData = await upsertTile(
            props.graphSlug,
            props.nodegroupGroupingNodeAlias,
            updatedTileData,
            props.tileData.tileid,
        );

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
            ref="form"
            :key="formKey"
            class="form"
            @submit="save"
        >
            <component
                :is="widget.component"
                v-for="widget in widgets"
                :key="widget.cardXNodeXWidgetData.id"
                :mode="props.mode"
                :graph-slug="props.graphSlug"
                :node-alias="widget.cardXNodeXWidgetData.node.alias"
                :card-x-node-x-widget-data="widget.cardXNodeXWidgetData"
                :value="
                    tileData.aliased_data[
                        widget.cardXNodeXWidgetData.node.alias
                    ]
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
</template>
<style scoped>
.form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
</style>
