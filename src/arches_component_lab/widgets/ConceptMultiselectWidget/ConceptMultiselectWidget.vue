<script setup lang="ts">
import ConceptMultiSelectWidgetEditor from "@/arches_component_lab/widgets/ConceptMultiselectWidget/components/ConceptMultiselectWidgetEditor.vue";
import ConceptMultiSelectWidgetViewer from "@/arches_component_lab/widgets/ConceptMultiselectWidget/components/ConceptMultiselectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { ConceptListValue } from "@/arches_component_lab/datatypes/concept-list/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    aliasedNodeData: ConceptListValue;
}>();

const emit = defineEmits(["update:value"]);
</script>

<template>
    <ConceptMultiSelectWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        :aliased-node-data="aliasedNodeData"
        @update:value="emit('update:value', $event)"
    />
    <ConceptMultiSelectWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="aliasedNodeData"
    />
</template>
