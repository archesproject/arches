<script setup lang="ts">
import arches from "arches";
import { computed, inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";

import ItemEditor from "@/components/ControlledListManager/ItemEditor.vue";
import ListCharacteristics from "@/components/ControlledListManager/ListCharacteristics.vue";
import ListHeader from "@/components/ControlledListManager/ListHeader.vue";
import ListTree from "@/components/ControlledListManager/ListTree.vue";
import { displayedListKey } from "@/components/ControlledListManager/const.ts";

import type { Language } from "@/types/arches";
import type { Ref } from "@/types/Ref";
import type { TreeSelectionKeys } from "primevue/tree/Tree";

const lightGray = "#f4f4f4";
const { $gettext } = useGettext();
const LIST_SUMMARY = $gettext("List Summary");

const { displayedList } = inject(displayedListKey);

// Key for selected item in Tree view, could be list or list item
// e.g. { "2000000-...": true }
const selectedKey: Ref<typeof TreeSelectionKeys> = ref({});
const selectedTreeNodeId = computed(() => {
    return Object.keys(selectedKey.value)[0] ?? null;
});
const selectedLanguage: Ref<Language> = ref(
    (arches.languages as Language[]).find(l => l.code === arches.activeLanguage)
);

const listOrItemView = computed(() => {
    if (selectedKey.value === null  || displayedList.value === null) {
        return ListCharacteristics;
    }
    const selectedTreeNodeId = Object.keys(selectedKey.value)[0];
    if (!selectedTreeNodeId || selectedTreeNodeId === displayedList.value.id) {
        return ListCharacteristics;
    }
    return ItemEditor;
});
</script>

<template>
    <div class="list-editor-container">
        <ListHeader />
        <Splitter
            v-if="displayedList"
            :pt="{
                root: { style: { height: '97%' } },
                gutter: { style: { background: lightGray } },
                gutterHandler: { style: { background: lightGray } },
            }"
        >
            <SplitterPanel
                :size="40"
                :min-size="25"
                :pt="{
                    root: { style: { display: 'flex', flexDirection: 'column' } },
                }"
            >
                <h3>{{ LIST_SUMMARY }}</h3>
                <!-- Use a key so that on list switch, the expandAll() in ListTree.setup runs -->
                <ListTree
                    :key="displayedList.id"
                    v-model:selected-key="selectedKey"
                    v-model:selected-language="selectedLanguage"
                    :displayed-list
                />
            </SplitterPanel>
            <SplitterPanel
                :size="60"
                :min-size="25"
            >
                <component
                    :is="listOrItemView"
                    :key="selectedTreeNodeId"
                    :item-id="selectedTreeNodeId"
                    :selected-language="selectedLanguage"
                />
            </SplitterPanel>
        </Splitter>
    </div>
</template>

<style scoped>
.list-editor-container {
    display: flex;
    flex-direction: column;
    height: 100%;
}
h3 {
    font-size: 1.5rem;
    margin: 1rem;
}
.p-splitter-panel {
    margin: 1rem;
    overflow-y: auto;
}
</style>
