<script setup lang="ts">
import type { ConceptValue } from "@/arches_component_lab/datatypes/concept/types.ts";

const { aliasedNodeData } = defineProps<{
    aliasedNodeData: ConceptValue;
}>();
</script>
<template>
    <div>
        {{ aliasedNodeData.display_value }}
    </div>
</template>
