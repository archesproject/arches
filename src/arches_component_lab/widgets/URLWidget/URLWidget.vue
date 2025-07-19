<script setup lang="ts">
import URLWidgetEditor from "@/arches_component_lab/widgets/URLWidget/components/URLWidgetEditor.vue";
import URLWidgetViewer from "@/arches_component_lab/widgets/URLWidget/components/URLWidgetViewer.vue";

import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants.ts";

import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";
import type { WidgetMode } from "@/arches_component_lab/widgets/types.ts";
import type { URLValue } from "@/arches_component_lab/datatypes/url/types";

const { mode, nodeAlias, graphSlug, cardXNodeXWidgetData, value } =
    defineProps<{
        mode: WidgetMode;
        nodeAlias: string;
        graphSlug: string;
        cardXNodeXWidgetData: CardXNodeXWidget;
        value: URLValue | null | undefined;
    }>();

console.log("URLWidget.vue", {
    mode,
    nodeAlias,
    graphSlug,
    cardXNodeXWidgetData,
    value,
});

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
