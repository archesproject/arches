<script setup lang="ts">
import { onMounted, ref, useTemplateRef } from "vue";

import ResourceInstanceSelectWidgetEditor from "@/arches_component_lab/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetEditor.vue";
import ResourceInstanceSelectWidgetViewer from "@/arches_component_lab/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetViewer.vue";
import { fetchWidgetConfiguration } from "@/arches_component_lab/widgets/api.ts";
import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import type {
    ResourceInstanceReference,
    WidgetMode,
} from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    mode?: WidgetMode;
    initialValue?: ResourceInstanceReference[];
    configuration: {
        nodeAlias: string;
        graphSlug: string;
        createNew?: boolean; // option to create a new resource - only used in EDIT; default false/undefined
    };
}>();

const childConfiguration = ref();

interface ChildComponentInterface {
    rawValue: any;
    isDirty: boolean;
}

onMounted(async () => {
    const widgetConfig = await fetchWidgetConfiguration(
        props.configuration.graphSlug,
        props.configuration.nodeAlias,
    );

    childConfiguration.value = {
        ...props.configuration,
        ...widgetConfig,
    };
});

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
    <div v-if="childConfiguration">
        <label>{{ childConfiguration?.label }}</label>
        <div v-if="mode === EDIT">
            <ResourceInstanceSelectWidgetEditor
                ref="childRef"
                :initial-value="initialValue"
                :configuration="childConfiguration"
            />
        </div>
        <div v-if="mode === VIEW">
            <ResourceInstanceSelectWidgetViewer
                ref="childRef"
                :initial-value="initialValue"
                :configuration="childConfiguration"
            />
        </div>
    </div>
</template>
