<script setup lang="ts">
import { onMounted, ref } from "vue";

import ProgressSpinner from "primevue/progressspinner";

import ReferenceSelectWidgetEditor from "@/arches_controlled_lists/widgets/ReferenceSelectWidget/components/ReferenceSelectWidgetEditor.vue";
import ReferenceSelectWidgetViewer from "@/arches_controlled_lists/widgets/ReferenceSelectWidget/components/ReferenceSelectWidgetViewer.vue";

import {
    fetchWidgetData,
    fetchNodeData,
} from "@/arches_component_lab/widgets/api.ts";
import { EDIT, VIEW } from "@/arches_controlled_lists/widgets/constants.ts";

import type { WidgetMode } from "@/arches_controlled_lists/widgets/types.ts";
import type { ControlledListItem } from "@/arches_controlled_lists/types.ts";

const props = withDefaults(
    defineProps<{
        mode: WidgetMode;
        initialValue: ControlledListItem[] | undefined;
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

onMounted(async () => {
    widgetData.value = await fetchWidgetData(props.graphSlug, props.nodeAlias);
    nodeData.value = await fetchNodeData(props.graphSlug, props.nodeAlias);

    isLoading.value = false;
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
            <ReferenceSelectWidgetEditor
                :initial-value="initialValue"
                :widget-data="widgetData"
                :node-alias="props.nodeAlias"
                :graph-slug="props.graphSlug"
            />
        </div>
        <div v-if="mode === VIEW">
            <ReferenceSelectWidgetViewer :value="initialValue" />
        </div>
    </template>
</template>
