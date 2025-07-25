<script setup lang="ts">
import ResourceInstanceMultiselectWidgetEditor from "@/arches_component_lab/widgets/ResourceInstanceMultiselectWidget/components/ResourceInstanceMultiselectWidgetEditor.vue";
import ResourceInstanceMultiselectWidgetViewer from "@/arches_component_lab/widgets/ResourceInstanceMultiselectWidget/components/ResourceInstanceMultiselectWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { ResourceInstanceListValue } from "@/arches_component_lab/datatypes/resource-instance-list/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    value: ResourceInstanceListValue;
}>();

const emit = defineEmits(["update:isDirty", "update:value"]);
</script>

<template>
    <ResourceInstanceMultiselectWidgetEditor
        v-if="mode === EDIT"
        :graph-slug="graphSlug"
        :node-alias="nodeAlias"
        :value="value"
        @update:value="emit('update:value', $event)"
        @update:is-dirty="emit('update:isDirty', $event)"
    />
    <ResourceInstanceMultiselectWidgetViewer
        v-if="mode === VIEW"
        :value="value"
    />
</template>
