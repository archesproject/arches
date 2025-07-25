<script setup lang="ts">
import URLWidgetEditor from "@/arches_component_lab/widgets/URLWidget/components/URLWidgetEditor.vue";
import URLWidgetViewer from "@/arches_component_lab/widgets/URLWidget/components/URLWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidgetData } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";
import type { URLValue } from "@/arches_component_lab/datatypes/url/types";

defineProps<{
    mode: WidgetMode;
    nodeAlias: string;
    graphSlug: string;
    cardXNodeXWidgetData: CardXNodeXWidgetData;
    value: URLValue;
}>();

const emit = defineEmits(["update:isDirty", "update:value"]);
</script>

<template>
    <URLWidgetEditor
        v-if="mode === EDIT"
        :node-alias="nodeAlias"
        :value="value"
        @update:value="emit('update:value', $event)"
        @update:is-dirty="emit('update:isDirty', $event)"
    />
    <URLWidgetViewer
        v-if="mode === VIEW"
        :value="value"
    />
</template>
