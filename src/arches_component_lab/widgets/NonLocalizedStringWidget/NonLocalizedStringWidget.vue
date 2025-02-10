<script setup lang="ts">
import { useTemplateRef } from "vue";

import NonLocalizedStringWidgetEditor from "@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetEditor.vue";
import NonLocalizedStringWidgetViewer from "@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    configuration: {
        label: string;
    };
    initialValue: string | undefined;
    mode: WidgetMode;
}>();

interface ChildComponentInterface {
    rawValue: boolean;
    isDirty: boolean;
}

const childRef = useTemplateRef<ChildComponentInterface>("childRef");

defineExpose({
    get rawValue() {
        return childRef.value?.rawValue;
    },
    get isDirty() {
        return childRef.value?.isDirty;
    },
});
</script>

<template>
    <label>{{ configuration.label }}</label>

    <NonLocalizedStringWidgetEditor
        v-if="props.mode === EDIT"
        ref="childRef"
        :initial-value="props.initialValue"
    />
    <NonLocalizedStringWidgetViewer
        v-else-if="props.mode === VIEW"
        ref="childRef"
        :value="props.initialValue"
    />
</template>
