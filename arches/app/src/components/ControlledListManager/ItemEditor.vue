<script setup lang="ts">
import { computed } from "vue";
import ItemCharacteristic from "@/components/ControlledListManager/ItemCharacteristic.vue";
import LabelEditor from "@/components/ControlledListManager/LabelEditor.vue";

import type { ControlledList } from "@/types/ControlledListManager";

const props: {
    displayedList: ControlledList
    editable: boolean,
    itemId: string,
} = defineProps(["displayedList", "editable", "itemId"]);

const item = computed(() => {
    if (!props.displayedList) {
        return null;
    }
    return props.displayedList.items.find(item => item.id === props.itemId);
});
</script>

<template>
    <LabelEditor
        :item
        type="prefLabel"
    />
    <LabelEditor
        :item
        type="altLabel"
    />
    <LabelEditor
        :item
        type="URI"
        :style="{ marginBottom: 0 }"
    />
    <ItemCharacteristic
        :item
        :editable="true"
        field="uri"
        :style="{ display: 'flex', alignItems: 'center', width: '80%' }"
    />
</template>
