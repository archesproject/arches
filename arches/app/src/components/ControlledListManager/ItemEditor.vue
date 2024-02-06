<script setup lang="ts">
import ItemCharacteristic from "@/components/ControlledListManager/ItemCharacteristic.vue";
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
        :style="{ marginBottom: 0 }"
    />
    <ItemCharacteristic
        :item="props.item"
        :editable="true"
        field="uri"
        :style="{ display: 'flex', alignItems: 'center', width: '80%' }"
    />
</template>

<style scoped>
</style>
