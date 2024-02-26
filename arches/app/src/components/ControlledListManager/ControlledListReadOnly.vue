<script setup lang="ts">
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Splitter from "primevue/splitter";
import SplitterPanel from "primevue/splitterpanel";

import ControlledListSplash from "@/components/ControlledListManager/ControlledListSplash.vue";
import ItemEditor from "@/components/ControlledListManager/ItemEditor.vue";
import ListCharacteristics from "@/components/ControlledListManager/ListCharacteristics.vue";
import ListHeader from "@/components/ControlledListManager/ListHeader.vue";
import ListTree from "@/components/ControlledListManager/ListTree.vue";

import type { Ref } from "@/types/Ref";
import type { ControlledList } from "@/types/ControlledListManager";

const lightGray = "#f4f4f4";
const buttonGreen = "#10b981";
const buttonPink = "#ed7979";

const { $gettext } = useGettext();
const listSummary = $gettext("List Summary");
const listDetails = $gettext("List Details");
const manageList = $gettext("Manage List");
const deleteList = $gettext("Delete List");
const selectAList = $gettext('Select a list from the sidebar.');

const props: {
    displayedList: ControlledList;
    setEditing: (val: boolean) => void;
    deleteLists: () => Promise<void>;
} = defineProps(["displayedList", "setEditing", "deleteLists"]);

// todo, better name or flesh out with comment
const selectedKey: Ref = ref(null);

const listOrItemView = computed(() => {
    if (
        selectedKey.value === null || props.displayedList.id in selectedKey.value
    ) {
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
            <h3>{{ listSummary }}</h3>
            <!-- Use a key so that on list switch, the expandAll() in ListTree.setup runs-->
            <ListTree
                :key="props.displayedList.id"
                v-model="selectedKey"
                :displayed-list
                :set-editing
            />
        </SplitterPanel>
        <SplitterPanel
            :size="60"
            :min-size="25"
        >
            <h3 style="padding-bottom: 1rem; border-bottom: 1px solid;">
                {{ listDetails }}
            </h3>
            <!-- TODO: figure out why this needed ugly unwrapping like this -->
            <component
                :is="listOrItemView"
                :item-id="Object.keys(selectedKey ?? {})[0]"
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
            :label="manageList"
            raised
            @click="() => setEditing(true)"
        />
        <Button
            class="button delete"
            :label="deleteList"
            raised
            @click="() => { deleteLists([displayedList]) }"
        />
    </div>

    <ControlledListSplash
        v-else
        :description="selectAList"
    />
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
