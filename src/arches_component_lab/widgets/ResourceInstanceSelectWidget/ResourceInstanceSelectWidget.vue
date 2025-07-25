<script setup lang="ts">
import ResourceInstanceSelectWidgetEditor from "@/arches_component_lab/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetEditor.vue";
import ResourceInstanceSelectWidgetViewer from "@/arches_component_lab/widgets/ResourceInstanceSelectWidget/components/ResourceInstanceSelectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";
import type { ResourceInstanceValue } from "@/arches_component_lab/datatypes/resource-instance/types";

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    value: ResourceInstanceValue;
}>();

const emit = defineEmits(["update:isDirty", "update:value"]);
</script>

<template>
    <ResourceInstanceSelectWidgetEditor
        v-if="mode === EDIT"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        :value="value"
        @update:value="emit('update:value', $event)"
        @update:is-dirty="emit('update:isDirty', $event)"
    />
    <ResourceInstanceSelectWidgetViewer
        v-if="mode === VIEW"
        :value="value"
    />
</template>
