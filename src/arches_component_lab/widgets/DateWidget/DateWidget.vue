<script setup lang="ts">
import { useTemplateRef } from "vue";

import DateWidgetEditor from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetEditor.vue";
import DateWidgetViewer from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    configuration: {
        label: string;
        dateFormat: string;
    };
    initialValue: any | undefined;
    mode: WidgetMode;
}>();

interface ChildComponentInterface {
    rawValue: any;
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

    <DateWidgetEditor
        v-if="props.mode === EDIT"
        ref="childRef"
        :initial-value="props.initialValue"
        :configuration="props.configuration"
    />
    <DateWidgetViewer
        v-else-if="props.mode === VIEW"
        ref="childRef"
        :initial-value="props.initialValue"
        :configuration="props.configuration"
    />
</template>
