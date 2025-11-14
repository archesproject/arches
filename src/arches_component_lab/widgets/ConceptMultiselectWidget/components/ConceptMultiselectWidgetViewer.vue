<script setup lang="ts">
import type { ConceptListValue } from "@/arches_component_lab/datatypes/concept-list/types.ts";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: ConceptListValue | null;
}>();
</script>
<template>
    <div>
        {{ aliasedNodeData?.display_value }}
    </div>
</template>
