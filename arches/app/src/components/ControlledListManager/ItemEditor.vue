<script setup lang="ts">
import { computed } from "vue";
import { useGettext } from "vue3-gettext";

import ItemCharacteristic from "@/components/ControlledListManager/ItemCharacteristic.vue";
import LabelEditor from "@/components/ControlledListManager/LabelEditor.vue";

import { bestLabel } from "@/components/ControlledListManager/utils.ts";

import type { Language } from "@/types/arches";
import type { ControlledList, ControlledListItem } from "@/types/ControlledListManager";

const props: {
    displayedList: ControlledList
    editable: boolean,
    itemId: string,
    selectedLanguage: Language,
} = defineProps(["displayedList", "editable", "itemId", "selectedLanguage"]);

const { $gettext } = useGettext();

const item = computed(() => {
    if (!props.displayedList) {
        return null;
    }

    const recurse = (items: ControlledListItem[]) => {
        for (const item of items) {
            if (item.id === props.itemId) {
                return item;
            }
            for (const child of item.children) {
                const maybeFound = recurse([child]);
                if (maybeFound) {
                    const found = (maybeFound as ControlledListItem);
                    return found;
                }
            }
        }
    };

    return recurse(props.displayedList.items);
});
</script>

<template>
    <h3>{{ bestLabel(item, selectedLanguage.code).value }}</h3>
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

<style scoped>
h3 {
    font-size: 1.5rem;
    margin: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid;
}
</style>