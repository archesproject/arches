<script setup lang="ts">
import { onMounted, ref } from "vue";

import ProgressSpinner from "primevue/progressspinner";

import ReferenceSelectWidgetEditor from "@/arches_controlled_lists/widgets/ReferenceSelectWidget/components/ReferenceSelectWidgetEditor.vue";
import ReferenceSelectWidgetViewer from "@/arches_controlled_lists/widgets/ReferenceSelectWidget/components/ReferenceSelectWidgetViewer.vue";

import { fetchWidgetConfiguration } from "@/arches_component_lab/widgets/api.ts";
import { EDIT, VIEW } from "@/arches_controlled_lists/widgets/constants.ts";

import type {
    WidgetMode,
} from "@/arches_controlled_lists/widgets/types.ts";

const props = defineProps<{
    mode: WidgetMode;
    initialValue: any[];
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

    console.log("!!!!!!", configuration.value);

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
            <ReferenceSelectWidgetEditor
                :initial-value="initialValue"
                :configuration="configuration"
                :node-alias="props.nodeAlias"
                :graph-slug="props.graphSlug"
            />
        </div>
        <div v-if="mode === VIEW">
            <ReferenceSelectWidgetViewer
                :initial-value="initialValue"
                :configuration="configuration"
            />
        </div>
    </template>
</template>

