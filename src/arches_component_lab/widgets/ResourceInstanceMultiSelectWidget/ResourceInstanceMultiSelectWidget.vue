<script setup lang="ts">
import { onMounted, ref } from "vue";

import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";

import ResourceInstanceMultiSelectWidgetEditor from "@/arches_component_lab/widgets/ResourceInstanceMultiSelectWidget/components/ResourceInstanceMultiSelectWidgetEditor.vue";
import ResourceInstanceMultiSelectWidgetViewer from "@/arches_component_lab/widgets/ResourceInstanceMultiSelectWidget/components/ResourceInstanceMultiSelectWidgetViewer.vue";

import {
    fetchWidgetData,
    fetchNodeData,
} from "@/arches_component_lab/widgets/api.ts";
import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type {
    ResourceInstanceReference,
    WidgetMode,
} from "@/arches_component_lab/widgets/types.ts";

const props = withDefaults(
    defineProps<{
        mode: WidgetMode;
        initialValue: ResourceInstanceReference[] | undefined;
        nodeAlias: string;
        graphSlug: string;
        showLabel?: boolean;
    }>(),
    {
        showLabel: true,
    },
);

const isLoading = ref(true);
const nodeData = ref();
const widgetData = ref();
const configurationError = ref();

onMounted(async () => {
    try {
        widgetData.value = await fetchWidgetData(
            props.graphSlug,
            props.nodeAlias,
        );
        nodeData.value = await fetchNodeData(props.graphSlug, props.nodeAlias);
    } catch (error) {
        configurationError.value = error;
    } finally {
        isLoading.value = false;
    }
});
</script>

<template>
    <ProgressSpinner
        v-if="isLoading"
        style="width: 2em; height: 2em"
    />

    <template v-else>
        <label v-if="props.showLabel">
            <span>{{ widgetData.label }}</span>
            <span v-if="nodeData.isrequired && props.mode === EDIT">*</span>
        </label>

        <div v-if="mode === EDIT">
            <ResourceInstanceMultiSelectWidgetEditor
                :initial-value="initialValue"
                :node-alias="props.nodeAlias"
                :graph-slug="props.graphSlug"
            />
        </div>
        <div v-if="mode === VIEW">
            <ResourceInstanceMultiSelectWidgetViewer :value="initialValue" />
        </div>
        <Message
            v-if="configurationError"
            severity="error"
            size="small"
        >
            {{ configurationError.message }}
        </Message>
    </template>
</template>
