<script setup lang="ts">
import NonLocalizedStringWidgetEditor from "@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetEditor.vue";
import NonLocalizedStringWidgetViewer from "@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    configuration: {
        label: string;
        graphSlug: string;
        nodeAlias: string;
    };
    initialValue: string | undefined;
    mode: WidgetMode;
}>();
</script>

<template>
    <label>{{ configuration.label }}</label>

    <NonLocalizedStringWidgetEditor
        v-if="props.mode === EDIT"
        :initial-value="props.initialValue"
        :configuration="props.configuration"
    />
    <NonLocalizedStringWidgetViewer
        v-else-if="props.mode === VIEW"
        :value="props.initialValue"
    />
</template>
