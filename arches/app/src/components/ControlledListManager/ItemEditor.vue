<script setup lang="ts">
import LabelEditor from "@/components/ControlledListManager/LabelEditor.vue";

import type {
    ControlledListItem,
} from "@/types/ControlledListManager.d";

const props: {
    item: ControlledListItem;
} = defineProps(["item"]);
</script>

<template>
    <LabelEditor
        :item="props.item"
        type="prefLabel"
    />
    <LabelEditor
        :item="props.item"
        type="altLabel"
    />
    <LabelEditor
        :item="props.item"
        type="URI"
    />
</template>

<style scoped>
</style>
