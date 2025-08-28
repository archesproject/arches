<script setup lang="ts">
import ConceptRadioWidgetEditor from "@/arches_component_lab/widgets/ConceptRadioWidget/components/ConceptRadioWidgetEditor.vue";
import ConceptRadioWidgetViewer from "@/arches_component_lab/widgets/ConceptRadioWidget/components/ConceptRadioWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { ConceptRadioCardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { ConceptValue } from "@/arches_component_lab/datatypes/concept/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: ConceptRadioCardXNodeXWidgetData;
    aliasedNodeData: ConceptValue;
}>();

const emit = defineEmits(["update:isDirty", "update:value"]);
</script>

<template>
    <ConceptRadioWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        :aliased-node-data="aliasedNodeData"
        @update:value="emit('update:value', $event)"
    />
    <ConceptRadioWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="aliasedNodeData"
    />
</template>
