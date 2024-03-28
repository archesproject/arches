<script setup lang="ts">
import { inject, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Tree from "primevue/tree";

import LetterCircle from "@/components/ControlledListManager/LetterCircle.vue";
import ListTreeControls from "@/components/ControlledListManager/ListTreeControls.vue";
import { displayedRowKey, selectedLanguageKey } from "@/components/ControlledListManager/const.ts";
import { bestLabel } from "@/components/ControlledListManager/utils.ts";

import type { Ref } from "@/types/Ref";
import type {
    TreeContext,
    TreeExpandedKeys,
    TreeNode,
    TreeSelectionKeys,
} from "primevue/tree/Tree";

const tree: Ref<typeof TreeNode[]> = ref([]);
const selectedKeys: Ref<typeof TreeSelectionKeys> = ref({});
const expandedKeys: Ref<typeof TreeExpandedKeys> = ref({});

const { setDisplayedRow } = inject(displayedRowKey);
const selectedLanguage = inject(selectedLanguageKey);

const { $gettext } = useGettext();
const lightGray = "#f4f4f4"; // todo: import from theme somewhere

const onRowSelect = (node: typeof TreeNode) => {
    setDisplayedRow(node.data);
};
</script>

<template>
    <ListTreeControls
        v-model="tree"
        v-model:expanded-keys="expandedKeys"
        v-model:selected-keys="selectedKeys"
        :selected-keys
    />
    <Tree
        v-if="tree"
        v-model:selectionKeys="selectedKeys"
        :value="tree"
        :expanded-keys
        :filter="true"
        filter-mode="lenient"
        :filter-placeholder="$gettext('Find')"
        selection-mode="checkbox"
        :pt="{
            root: { style: { flexGrow: 1, margin: '1rem' } },
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
        @node-select="onRowSelect"
    >
        <template #nodeicon="slotProps">
            <LetterCircle :labelled="slotProps.node.data" />
        </template>
        <template #default="slotProps">
            {{ slotProps.node.data.name ?? bestLabel(slotProps.node.data, selectedLanguage.code).value }}
            <span v-if="slotProps.node.data.uri">
                (<a
                    :href="slotProps.node.data.uri"
                    target="_blank"
                    rel="noopener noreferrer"
                >{{ slotProps.node.data.uri }}</a>)
            </span>
        </template>
    </Tree>
</template>

<style scoped>
a {
    color: var(--blue-500);
}
</style>
