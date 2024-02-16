<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";

import Tree from "primevue/tree";

import type { Ref } from "vue";
import type { TreeContext, TreeNode } from "primevue/tree/TreeNode";

import type { Language } from "@/types/arches";
import type {
    ControlledList,
    ControlledListItem
} from "@/types/ControlledListManager.d";

const props: {
    displayedList: ControlledList;
    setEditing: (val: boolean) => void;
} = defineProps(["displayedList", "setEditing"]);

const selectedLanguage: Ref<Language> = ref(
    (arches.languages as Language[]).find(l => l.code === arches.activeLanguage)
);
const selectedKey: Ref<string | null> = ref(null);

const slateBlue = "#2d3c4b"; // todo: import from theme somewhere

const bestLabel = (item: ControlledListItem) => {
    const labelsInLang = item.labels.filter(l => l.language === selectedLanguage.value.code);
    const bestLabel = (
        labelsInLang.find(l => l.valuetype === "prefLabel")
        ?? labelsInLang.find(l => l.valuetype === "altLabel")
        ?? item.labels.find(l => l.valuetype === "prefLabel")
    );
    if (!bestLabel) {
        throw new Error();
    }
    return bestLabel;
};

function asNode(item: ControlledListItem): TreeNode {
    return {
        key: item.id,
        label: bestLabel(item).value,
        children: item.children.map(child => asNode(child)),
        data: item,
    };
}

const value = computed(() => {
    return props.displayedList.items.map(item => asNode(item));
});
</script>

<template>
    <Tree
        v-model:selectionKeys="selectedKey"
        :value
        :filter="true"
        filter-mode="lenient"
        selection-mode="single"
        :pt="{
            input: {
                placeholder: $gettext('Find'),
                style: { height: '3.5rem', fontSize: '14px' },
            },
            container: { style: { fontSize: '14px' }},
            content: ({ context }) : { context: TreeContext } => ({
                style: {
                    background: context.selected ? slateBlue : '',
                    height: '3.5rem',
                },
            }),
        }"
    >
        <template #default="slotProps">
            <span>
                {{ slotProps.node.label }}
                <span v-if="slotProps.node.data.uri">
                    (<a
                        :href="slotProps.node.data.uri"
                        target="_blank"
                        rel="noopener noreferrer"
                        :class="selectedKey && slotProps.node.data.id in selectedKey ? 'selected' : ''"
                    >{{ slotProps.node.data.uri }}</a>)
                </span>
            </span>
        </template>
    </Tree>
</template>

<style scoped>
a {
    color: var(--blue-500);
}
</style>
