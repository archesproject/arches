<script setup lang="ts">
import DateWidgetEditor from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetEditor.vue";
import DateWidgetViewer from "@/arches_component_lab/widgets/DateWidget/components/DateWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    configuration: {
        dateFormat: string;
        graphSlug: string;
        label: string;
        nodeAlias: string;
    };
    initialValue: Date | undefined;
    mode: WidgetMode;
}>();
</script>

<template>
    <label>{{ configuration.label }}</label>

    <DateWidgetEditor
        v-if="props.mode === EDIT"
        :initial-value="props.initialValue"
        :configuration="props.configuration"
    />
    <DateWidgetViewer
        v-else-if="props.mode === VIEW"
        :value="props.initialValue"
        :configuration="props.configuration"
    />
</template>
