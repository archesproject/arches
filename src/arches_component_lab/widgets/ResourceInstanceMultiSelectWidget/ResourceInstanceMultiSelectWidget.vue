<script setup lang="ts">
import { onMounted, ref } from "vue";

import ProgressSpinner from "primevue/progressspinner";

import ResourceInstanceMultiSelectWidgetEditor from "@/arches_component_lab/widgets/ResourceInstanceMultiSelectWidget/components/ResourceInstanceMultiSelectWidgetEditor.vue";
import ResourceInstanceMultiSelectWidgetViewer from "@/arches_component_lab/widgets/ResourceInstanceMultiSelectWidget/components/ResourceInstanceMultiSelectWidgetViewer.vue";

import { fetchWidgetConfiguration } from "@/arches_component_lab/widgets/api.ts";
import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type {
    ResourceInstanceReference,
    WidgetMode,
} from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    mode: WidgetMode;
    initialValue: ResourceInstanceReference[];
    nodeAlias: string;
    graphSlug: string;
}>();

const isLoading = ref(true);
const configuration = ref();

onMounted(async () => {
    configuration.value = await fetchWidgetConfiguration(
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
        <label>{{ configuration.label }}</label>

        <div v-if="mode === EDIT">
            <ResourceInstanceMultiSelectWidgetEditor
                :initial-value="initialValue"
                :configuration="configuration"
                :node-alias="props.nodeAlias"
                :graph-slug="props.graphSlug"
            />
        </div>
        <div v-if="mode === VIEW">
            <ResourceInstanceMultiSelectWidgetViewer
                :initial-value="initialValue"
                :configuration="configuration"
            />
        </div>
    </template>
</template>
