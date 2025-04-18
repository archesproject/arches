<script setup lang="ts">
import { onMounted, ref } from "vue";

import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";

import DateWidgetEditor from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetEditor.vue";
import DateWidgetViewer from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetViewer.vue";

import {
    fetchWidgetData,
    fetchNodeData,
} from "@/arches_component_lab/widgets/api.ts";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = withDefaults(
    defineProps<{
        mode: WidgetMode;
        initialValue: string | null | undefined;
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
        nodeData.value = await fetchNodeData(props.graphSlug, props.nodeAlias);
        widgetData.value = await fetchWidgetData(
            props.graphSlug,
            props.nodeAlias,
        );
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

        <DateWidgetEditor
            v-if="props.mode === EDIT"
            :initial-value="props.initialValue"
            :graph-slug="props.graphSlug"
            :node-alias="props.nodeAlias"
            :widget-data="widgetData"
        />
        <DateWidgetViewer
            v-else-if="props.mode === VIEW"
            :initial-value="props.initialValue"
            :widget-data="widgetData"
        />
    </template>
    <Message
        v-if="configurationError"
        severity="error"
        size="small"
    >
        {{ configurationError.message }}
    </Message>
</template>
