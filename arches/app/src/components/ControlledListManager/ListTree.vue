<script setup lang="ts">
import arches from "arches";
import { computed, ref } from "vue";
import { useGettext } from "vue3-gettext";

import Button from "primevue/button";
import Dropdown from "primevue/dropdown";
import Tree from "primevue/tree";

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

const selectedLanguage: Ref<Language> = ref(
    (arches.languages as Language[]).find(l => l.code === arches.activeLanguage)
);
const selectedKey: Ref<typeof TreeSelectionKeys> = defineModel({ default: {} });
const expandedKeys: Ref<typeof TreeExpandedKeys> = ref({});
const editing: Ref<boolean> = defineModel("editing");

const { $gettext } = useGettext();

const LIST_LABEL = $gettext("Controlled List");
const GUIDE_LABEL = $gettext("Guide Item");
const INDEXABLE_LABEL = $gettext("Indexable Item");
const MANAGE_LIST = $gettext("Manage List");
const RETURN = $gettext("Return to List Manager");

const slateBlue = "#2d3c4b"; // todo: import from theme somewhere
const lightGray = "#f4f4f4";
const buttonGreen = "#10b981";

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
        icon: item.guide ? "fa fa-folder-open" : "fa fa-hand-pointer-o",
        iconLabel: item.guide ? GUIDE_LABEL : INDEXABLE_LABEL,
    };
}

function listAsNode(list: ControlledList): typeof TreeNode {
    return {
        key: list.id,
        label: list.name,
        children: list.items.map(item => itemAsNode(item)),
        data: list,
        icon: "fa fa-list",
        iconLabel: LIST_LABEL,
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
                input: { style: { fontSize: 'small', textAlign: 'center' } },
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
            root: { style: { flexGrow: 1 } },
            input: {
                placeholder: $gettext('Find'),
                style: { height: '3.5rem', fontSize: '14px' },
            },
            container: { style: { fontSize: '14px' } },
            content: ({ context }) : { context: TreeContext } => ({
                style: {
                    background: context.selected ? slateBlue : '',
                    height: '3.5rem',
                },
                tabindex: '0',
            }),
            label: { style: { textWrap: 'nowrap' } },
            nodeicon: { ariaHidden: 'true' },
        }"
    >
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
    <div
        :style="{ background: lightGray }"
    >
        <Button
            class="button manage-list"
            :label="editing ? RETURN : MANAGE_LIST"
            raised
            @click="editing = !editing"
        />
    </div>
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
.button.manage-list {
    background: v-bind(buttonGreen);
    border: 1px solid v-bind(buttonGreen);
}
</style>
