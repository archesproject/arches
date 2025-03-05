<script setup lang="ts">
import { onMounted, ref } from "vue";

import ProgressSpinner from "primevue/progressspinner";

import ResourceInstanceMultiSelectWidgetEditor from "@/arches_component_lab/widgets/ResourceInstanceMultiSelectWidget/components/ResourceInstanceMultiSelectWidgetEditor.vue";
import ResourceInstanceMultiSelectWidgetViewer from "@/arches_component_lab/widgets/ResourceInstanceMultiSelectWidget/components/ResourceInstanceMultiSelectWidgetViewer.vue";

import {
    fetchWidget,
    fetchNode,
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
const nodeRef = ref();
const widgetRef = ref();

onMounted(async () => {
    widgetRef.value = await fetchWidget(
        props.graphSlug,
        props.nodeAlias,
    );
    nodeRef.value = await fetchNode(
        props.graphSlug,
        props.nodeAlias,
    );

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
            <span>{{ widgetRef.label }}</span>
            <span v-if="nodeRef.isrequired && props.mode === EDIT">*</span>
        </label>

        <div v-if="mode === EDIT">
            <ResourceInstanceMultiSelectWidgetEditor
                :initial-value="initialValue"
                :configuration="widgetRef.config"
                :node-alias="props.nodeAlias"
                :graph-slug="props.graphSlug"
            />
        </div>
        <div v-if="mode === VIEW">
            <ResourceInstanceMultiSelectWidgetViewer :value="initialValue" />
        </div>
    </template>
</template>
