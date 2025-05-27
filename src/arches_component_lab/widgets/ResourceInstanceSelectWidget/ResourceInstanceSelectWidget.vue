<script setup lang="ts">
import { onMounted, ref } from "vue";

import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";

import ResourceInstanceSelectWidgetEditor from "@/arches_component_lab/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetEditor.vue";
import ResourceInstanceSelectWidgetViewer from "@/arches_component_lab/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetViewer.vue";

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
        initialValue: ResourceInstanceReference | null | undefined;
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

        <div :class="[props.nodeAlias, props.graphSlug].join(' ')">
            <ResourceInstanceSelectWidgetEditor
                v-if="mode === EDIT"
                ref="editor"
                :initial-value="initialValue"
                :node-alias="props.nodeAlias"
                :graph-slug="props.graphSlug"
            />
            <ResourceInstanceSelectWidgetViewer
                v-else-if="mode === VIEW"
                :value="initialValue"
            />
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
