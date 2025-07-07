<script setup lang="ts">
import ResourceInstanceMultiSelectWidgetEditor from "@/arches_component_lab/widgets/ResourceInstanceMultiSelectWidget/components/ResourceInstanceMultiSelectWidgetEditor.vue";
import ResourceInstanceMultiSelectWidgetViewer from "@/arches_component_lab/widgets/ResourceInstanceMultiSelectWidget/components/ResourceInstanceMultiSelectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type {
    ResourceInstanceReference,
    WidgetMode,
} from "@/arches_component_lab/widgets/types.ts";

const props = defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: CardXNodeXWidget;
    value: ResourceInstanceReference[] | null | undefined;
}>();

const emit = defineEmits(["update:isDirty", "update:value"]);
</script>

<template>
    <ResourceInstanceMultiSelectWidgetEditor
        v-if="props.mode === EDIT"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        :value="props.value"
        @update:value="emit('update:value', $event)"
        @update:is-dirty="emit('update:isDirty', $event)"
    />
    <ResourceInstanceMultiSelectWidgetViewer
        v-if="props.mode === VIEW"
        :card-x-node-x-widget-data="cardXNodeXWidgetData"
        :value="props.value"
    />
</template>
