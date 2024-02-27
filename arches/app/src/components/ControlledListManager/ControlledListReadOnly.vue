<script setup lang="ts">
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";

import ItemEditor from "@/components/ControlledListManager/ItemEditor.vue";
import ListCharacteristics from "@/components/ControlledListManager/ListCharacteristics.vue";
import ListHeader from "@/components/ControlledListManager/ListHeader.vue";
import ListTree from "@/components/ControlledListManager/ListTree.vue";

import type { Ref } from "@/types/Ref";
import type { TreeSelectionKeys } from "primevue/tree/Tree";
import type { ControlledList } from "@/types/ControlledListManager";

const lightGray = "#f4f4f4";
const buttonGreen = "#10b981";
const buttonPink = "#ed7979";

const { $gettext } = useGettext();
const LIST_SUMMARY = $gettext("List Summary");
const MANAGE_LIST = $gettext("Manage List");
const DELETE_LIST = $gettext("Delete List");

const props: {
    displayedList: ControlledList;
    deleteLists: () => Promise<void>;
} = defineProps(["displayedList", "deleteLists"]);

const editing: Ref<boolean> = defineModel("editing");

// Key for selected item in Tree view, could be list or list item
// e.g. { "2000000-...": true }
const selectedKey: Ref<typeof TreeSelectionKeys> = ref({[props.displayedList.id]: true});
const selectedTreeNodeId = computed(() => {
    return Object.keys(selectedKey.value)[0] ?? null;
});

const listOrItemView = computed(() => {
    if (selectedKey.value === null) {
        return ListCharacteristics;
    }
    const selectedTreeNodeId = Object.keys(selectedKey.value)[0] ?? null;
    if (selectedTreeNodeId  === props.displayedList.id) {
        return ListCharacteristics;
    }
    return ItemEditor;
});
</script>

<template>
    <ListHeader
        :displayed-list="props.displayedList"
        :is-item-editor="false"
    />

    <Splitter
        v-if="props.displayedList"
        :pt="{
            gutter: { style: { background: lightGray } },
            gutterHandler: { style: { background: lightGray } },
        }"
    >
        <SplitterPanel
            :size="40"
            :min-size="25"
        >
            <h3>{{ LIST_SUMMARY }}</h3>
            <!-- Use a key so that on list switch, the expandAll() in ListTree.setup runs -->
            <ListTree
                :key="props.displayedList.id"
                v-model="selectedKey"
                :displayed-list
            />
        </SplitterPanel>
        <SplitterPanel
            :size="60"
            :min-size="25"
        >
            <component
                :is="listOrItemView"
                :item-id="selectedTreeNodeId"
                :key="selectedTreeNodeId"
                :displayed-list
                :editable="false"
            />
        </SplitterPanel>
    </Splitter>

    <div
        v-if="props.displayedList"
        :style="{ background: lightGray }"
    >
        <Button
            class="button manage-list"
            :label="MANAGE_LIST"
            raised
            @click="editing = true"
        />
        <Button
            class="button delete"
            :label="DELETE_LIST"
            raised
            @click="() => { deleteLists([displayedList]) }"
        />
    </div>
</template>

<style scoped>
h3 {
    font-size: 1.5rem;
    margin: 1rem;
}
.p-splitter {
    max-height: calc(100% - 135px);
}
.p-splitter-panel {
    margin: 1rem;
}
.button {
    font-size: inherit;
    height: 4rem;
    margin: 0.5rem;
    justify-content: center;
    font-weight: 600;
    color: white;
    text-wrap: nowrap;
}
.button.manage-list {
    background: v-bind(buttonGreen);
    border: 1px solid v-bind(buttonGreen);
}
.button.delete {
    background: v-bind(buttonPink);
    border: 1px solid v-bind(buttonPink);
}
</style>
