<script setup lang="ts">
import { onMounted, ref } from "vue";

import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";

import NonLocalizedStringWidgetEditor from "@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetEditor.vue";
import NonLocalizedStringWidgetViewer from "@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import {
    fetchWidgetData,
    fetchNodeData,
} from "@/arches_component_lab/widgets/api.ts";

import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = withDefaults(
    defineProps<{
        mode: WidgetMode;
        initialValue: string | undefined;
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

        <NonLocalizedStringWidgetEditor
            v-if="props.mode === EDIT"
            :initial-value="initialValue"
            :graph-slug="props.graphSlug"
            :node-alias="props.nodeAlias"
        />
        <NonLocalizedStringWidgetViewer
            v-else-if="props.mode === VIEW"
            :value="props.initialValue"
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
