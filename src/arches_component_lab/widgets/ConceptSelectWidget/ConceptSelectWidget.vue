<script setup lang="ts">
import ConceptSelectWidgetEditor from "@/arches_component_lab/widgets/ConceptSelectWidget/components/ConceptSelectWidgetEditor.vue";
import ConceptSelectWidgetViewer from "@/arches_component_lab/widgets/ConceptSelectWidget/components/ConceptSelectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { ConceptValue } from "@/arches_component_lab/datatypes/concept/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    aliasedNodeData: ConceptValue;
}>();

const emit = defineEmits(["update:value"]);
</script>

<template>
    <ConceptSelectWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        :aliased-node-data="aliasedNodeData"
        @update:value="emit('update:value', $event)"
    />
    <ConceptSelectWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="aliasedNodeData"
    />
</template>
