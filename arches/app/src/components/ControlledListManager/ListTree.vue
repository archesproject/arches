<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Dropdown from "primevue/dropdown";
import Tree from "primevue/tree";

import type { Ref } from "vue";
import type { TreeContext, TreeExpandedKeys, TreeNode } from "primevue/tree/Tree";

import type { Language } from "@/types/arches";
import type {
    ControlledList,
    ControlledListItem
} from "@/types/ControlledListManager";

const props: {
    displayedList: ControlledList;
    setEditing: (val: boolean) => void;
} = defineProps(["displayedList", "setEditing"]);

const selectedLanguage: Ref<Language> = ref(
    (arches.languages as Language[]).find(l => l.code === arches.activeLanguage)
);
const selectedKey: Ref<string | null> = ref(null);
const expandedKeys: Ref<typeof TreeExpandedKeys> = ref({});
const { $gettext } = useGettext();

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

function itemAsNode(item: ControlledListItem): typeof TreeNode {
    return {
        key: item.id,
        label: bestLabel(item).value,
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
    if (id === selectedKey.value) {
        return "selected";
    }
    return "";
};

const expandAll = () => {
    for (const node of controlledListItemsTree.value) {
        expandNode(node);
    }

    expandedKeys.value = { ...expandedKeys.value };
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
                input: { style: { fontSize: 'small' } },
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
                        :class="itemClass(slotProps.node.data.id)"
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
</style>
