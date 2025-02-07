<script setup lang="ts">
import NonLocalizedStringWidgetEditor from '@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetEditor.vue';
import NonLocalizedStringWidgetViewer from '@/arches_component_lab/widgets/NonLocalizedStringWidget/components/NonLocalizedStringWidgetViewer.vue';

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";
import type { WidgetMode } from '@/arches_component_lab/widgets/types.ts';

const props = defineProps<{
    mode: WidgetMode;
}>();
</script>

<template>
    <NonLocalizedStringWidgetEditor
        v-if="props.mode === EDIT"
    />
    <NonLocalizedStringWidgetViewer
        v-else-if="props.mode === VIEW"
    />
</template>