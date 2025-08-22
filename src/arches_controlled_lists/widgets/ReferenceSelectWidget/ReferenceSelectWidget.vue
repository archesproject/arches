<script setup lang="ts">
import ReferenceSelectWidgetEditor from "@/arches_controlled_lists/widgets/ReferenceSelectWidget/components/ReferenceSelectWidgetEditor.vue";
import ReferenceSelectWidgetViewer from "@/arches_controlled_lists/widgets/ReferenceSelectWidget/components/ReferenceSelectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

import type {
    ReferenceSelectDatatypeCardXNodeXWidgetData,
    ReferenceSelectValue,
} from "@/arches_controlled_lists/datatypes/reference-select/types.ts";

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: ReferenceSelectDatatypeCardXNodeXWidgetData;
    aliasedNodeData: ReferenceSelectValue;
}>();

const emit = defineEmits(["update:value"]);
</script>

<template>
    <ReferenceSelectWidgetEditor
        v-if="mode === EDIT"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :aliased-node-data="aliasedNodeData"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        @update:value="emit('update:value', $event)"
    />
    <ReferenceSelectWidgetViewer
        v-if="mode === VIEW"
        :aliased-node-data="aliasedNodeData"
    />
</template>
