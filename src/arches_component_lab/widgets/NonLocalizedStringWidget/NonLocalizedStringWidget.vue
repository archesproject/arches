<script setup lang="ts">
import { onMounted, ref } from "vue";

import ProgressSpinner from "primevue/progressspinner";

import NonLocalizedStringWidgetEditor from "@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetEditor.vue";
import NonLocalizedStringWidgetViewer from "@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import { fetchWidgetConfiguration, fetchNodeConfiguration } from "@/arches_component_lab/widgets/api.ts";

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
const configuration = ref();

onMounted(async () => {
    const widgetConfiguration = await fetchWidgetConfiguration(
        props.graphSlug,
        props.nodeAlias,
    );

    const nodeConfiguration = await fetchNodeConfiguration(
        props.graphSlug,
        props.nodeAlias,
    );

    configuration.value = {
        ...nodeConfiguration,
        ...widgetConfiguration,
    };

    isLoading.value = false;
});
</script>

<template>
    <ProgressSpinner
        v-if="isLoading"
        style="width: 2em; height: 2em"
    />
    <template v-else>
        <label v-if="props.showLabel">{{ configuration.label }}</label>
        <span v-if="configuration.isRequired">*</span>

        <NonLocalizedStringWidgetEditor
            v-if="props.mode === EDIT"
            :initial-value="initialValue"
            :graph-slug="props.graphSlug"
            :node-alias="props.nodeAlias"
            :configuration="configuration"
        />
        <NonLocalizedStringWidgetViewer
            v-else-if="props.mode === VIEW"
            :value="props.initialValue"
        />
    </template>
</template>
