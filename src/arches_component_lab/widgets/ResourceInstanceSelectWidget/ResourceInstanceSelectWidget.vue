<script setup lang="ts">
import { useTemplateRef } from "vue";

import ResourceInstanceSelectWidgetEditor from "@/arches_component_lab/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetEditor.vue";
import ResourceInstanceSelectWidgetViewer from "@/arches_component_lab/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetViewer.vue";

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
    <div v-if="mode === EDIT">
        <ResourceInstanceSelectWidgetEditor
            :initial-value="initialValue"
            :configuration="configuration"
        />
    </div>
    <div v-if="mode === VIEW">
        <ResourceInstanceSelectWidgetViewer
            :initial-value="initialValue"
            :configuration="configuration"
        />
    </div>
</template>
