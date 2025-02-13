<script setup lang="ts">
import { onMounted, ref } from "vue";

import ProgressSpinner from "primevue/progressspinner";

import DateWidgetEditor from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetEditor.vue";
import DateWidgetViewer from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetViewer.vue";

import { fetchWidgetConfiguration } from "@/arches_component_lab/widgets/api.ts";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    graphSlug: string;
    nodeAlias: string;
    initialValue: Date | undefined;
    mode: WidgetMode;
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

        <DateWidgetEditor
            v-if="props.mode === EDIT"
            :initial-value="props.initialValue"
            :configuration="configuration"
        />
        <DateWidgetViewer
            v-else-if="props.mode === VIEW"
            :value="props.initialValue"
            :configuration="configuration"
        />
    </template>
</template>
