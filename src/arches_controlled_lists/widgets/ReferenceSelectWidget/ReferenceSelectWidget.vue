<script setup lang="ts">
import { useTemplateRef } from "vue";

import ReferenceSelectWidgetEditor from "@/arches_controlled_lists/widgets/ReferenceSelectWidget/components/ReferenceSelectWidgetEditor.vue";
import ReferenceSelectWidgetViewer from "@/arches_controlled_lists/widgets/ReferenceSelectWidget/components/ReferenceSelectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    mode?: WidgetMode;
    initialValue?: any[];
    configuration: {
        label: string;
        placeholder: string;
        nodeAlias: string;
        multiValue: boolean;
    };
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
    <label>{{ props.configuration.label }}</label>

    <ReferenceSelectWidgetEditor
        v-if="props.mode === EDIT"
        ref="childRef"
        :initial-value="initialValue"
        :configuration="props.configuration"
    />
</template>
