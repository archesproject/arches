<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Dropdown from "primevue/dropdown";
import Tree from "primevue/tree";

import LetterCircle from "@/components/ControlledListManager/LetterCircle.vue";
import { bestLabel } from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "@/types/Ref";
import type {
    TreeContext,
    TreeExpandedKeys,
    TreeNode,
    TreeSelectionKeys,
} from "primevue/tree/Tree";

import type { Language } from "@/types/arches";
import type {
    ControlledList,
    ControlledListItem
} from "@/types/ControlledListManager";

const props: { displayedList: ControlledList } = defineProps(["displayedList"]);

const selectedKey: Ref<typeof TreeSelectionKeys> = defineModel("selectedKey");
const expandedKeys: Ref<typeof TreeExpandedKeys> = ref({});
const selectedLanguage: Ref<Language> = defineModel("selectedLanguage");

const { $gettext } = useGettext();
const lightGray = "#f4f4f4"; // todo: import from theme somewhere

function itemAsNode(item: ControlledListItem): typeof TreeNode {
    return {
        key: item.id,
        label: bestLabel(item, selectedLanguage.value.code).value,
        children: item.children.map(child => itemAsNode(child)),
        data: item,
    };
}

function listAsNode(list: ControlledList): typeof TreeNode {
    return {
        key: list.id,
        label: list.name,
        children: list.items.map(item => itemAsNode(item)),
        data: list,
    };
}

const controlledListItemsTree = computed(() => {
    return [listAsNode(props.displayedList)];
});

const itemClass = (id: string) => {
    if (id in selectedKey.value) {
        return "selected";
    }
    return "";
};

const expandAll = () => {
    for (const node of controlledListItemsTree.value) {
        expandNode(node);
    }
};

const collapseAll = () => {
    expandedKeys.value = {};
};

const expandNode = (node: typeof TreeNode) => {
    if (node.children && node.children.length) {
        expandedKeys.value[node.key] = true;

        for (const child of node.children) {
            expandNode(child);
        }
    }
};

// Runs on list switch if the parent remembers to send a :key
expandAll();
</script>

<template>
    <div class="controls">
        <Button
            class="control"
            type="button"
            icon="fa fa-plus"
            :label="$gettext('Expand')"
            @click="expandAll"
        />
        <Button
            class="control"
            type="button"
            icon="fa fa-minus"
            :label="$gettext('Collapse')"
            @click="collapseAll"
        />
        <Dropdown
            v-model="selectedLanguage"
            :options="arches.languages"
            option-label="name"
            :placeholder="$gettext('Language')"
            checkmark
            :highlight-on-select="false"
            :pt="{
                root: { class: 'control' },
                input: { style: { fontFamily: 'inherit', fontSize: 'small', textAlign: 'center' } },
                itemLabel: { style: { fontSize: 'small' } },
            }"
        />
    </div>
    <Tree
        v-model:selectionKeys="selectedKey"
        :value="controlledListItemsTree"
        :expanded-keys
        :filter="true"
        filter-mode="lenient"
        :filter-placeholder="$gettext('Find')"
        selection-mode="single"
        :pt="{
            root: { style: { flexGrow: 1 } },
            input: {
                style: { height: '3.5rem', fontSize: '14px' },
            },
            container: { style: { fontSize: '14px' } },
            content: ({ context }) : { context: TreeContext } => ({
                style: {
                    background: context.selected ? lightGray : '',
                    height: '3.5rem',
                },
            }),
            label: { style: { textWrap: 'nowrap', marginLeft: '0.5rem' } },
        }"
    >
        <template #nodeicon="slotProps">
            <LetterCircle :labelled="slotProps.node.data" />
        </template>
        <template #default="slotProps">
            {{ slotProps.node.label }}
            <span v-if="slotProps.node.data.uri">
                (<a
                    :href="slotProps.node.data.uri"
                    target="_blank"
                    rel="noopener noreferrer"
                    :class="itemClass(slotProps.node.data.id)"
                >{{ slotProps.node.data.uri }}</a>)
            </span>
        </template>
    </Tree>
</template>

<style scoped>
a {
    color: var(--blue-500);
}
.controls {
    display: flex;
    background: #f3fbfd;
    padding: 1rem;
    gap: 0.5rem;
}
.control {
    flex: 0.33;
    border: 0;
    background: lightgray;
    font-size: small;
}
.button {
    font-size: small;
    height: 4rem;
    margin: 0.5rem;
    justify-content: center;
    font-weight: 600;
    color: white;
    text-wrap: nowrap;
}
</style>
