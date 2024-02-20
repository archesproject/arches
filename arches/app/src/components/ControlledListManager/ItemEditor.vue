<script setup lang="ts">
import ItemCharacteristic from "@/components/ControlledListManager/ItemCharacteristic.vue";
import LabelEditor from "@/components/ControlledListManager/LabelEditor.vue";

import type {
    ControlledListItem, LanguageMap,
} from "@/types/ControlledListManager.d";

const props: {
    item: ControlledListItem;
    languageMap: LanguageMap;
} = defineProps(["item", "languageMap"]);
</script>

<template>
    <LabelEditor
        :item="props.item"
        :language-map
        type="prefLabel"
    />
    <LabelEditor
        :item="props.item"
        :language-map
        type="altLabel"
    />
    <LabelEditor
        :item="props.item"
        :language-map
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
