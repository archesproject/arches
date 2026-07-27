<script setup lang="ts">
import { computed, inject, onMounted, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useGettext } from "vue3-gettext";
import { useToast } from "primevue/usetoast";

import InputText from "primevue/inputtext";
import Message from "primevue/message";
import Tree from "primevue/tree";

import {
    DEFAULT_ERROR_TOAST_LIFE,
    ERROR,
    displayedRowKey,
    selectedLanguageKey,
} from "@/arches_controlled_lists/constants.ts";
import { routeNames } from "@/arches_controlled_lists/routes.ts";
import {
    findNodeInTree,
    listAsNode,
    nodeIsList,
} from "@/arches_controlled_lists/utils.ts";
import { useCappedTreeFilter } from "@/arches_controlled_lists/components/tree/utils/capped-filter.ts";
import { fetchFilteredList } from "@/arches_controlled_lists/api.ts";
import { useListStore } from "@/arches_controlled_lists/stores/useListStore.ts";
import ListTreeControls from "@/arches_controlled_lists/components/tree/ListTreeControls.vue";
import TreeRow from "@/arches_controlled_lists/components/tree/TreeRow.vue";

import type { Ref } from "vue";
import type { RouteLocationNormalizedLoadedGeneric } from "vue-router";
import type { TreePassThroughMethodOptions } from "primevue/tree";
import type { TreeExpandedKeys, TreeSelectionKeys } from "primevue/tree";
import type { TreeNode } from "primevue/treenode";
import type {
    ControlledList,
    ControlledListItem,
    Language,
    RowSetter,
    Value,
} from "@/arches_controlled_lists/types";

const FILTER_DEBOUNCE_MS = 250;
const FILTER_RENDER_CAP = 2500;

const toast = useToast();
const { $gettext } = useGettext();

const moveLabels = Object.freeze({
    addChild: $gettext("Add child item"),
    moveUp: $gettext("Move item up"),
    moveDown: $gettext("Move item down"),
    changeParent: $gettext("Change item parent"),
});
const iconLabels = Object.freeze({
    list: $gettext("List"),
    item: $gettext("Item"),
});
const FILTER_PLACEHOLDER = $gettext("Find");
const FILTER_CAPPED_MESSAGE = $gettext(
    "Too many matches to display. Please refine your query.",
);

const listStore = useListStore();
const selectedLanguage = inject(selectedLanguageKey) as Ref<Language>;

const selectedKeys: Ref<TreeSelectionKeys> = ref({});
const expandedKeys: Ref<TreeExpandedKeys> = ref({});
const movingItem: Ref<TreeNode | undefined> = ref();
const shouldCopyChildren = ref(true);
const isMultiSelecting = ref(false);
const filterValue = ref("");
const loadingNodeKeys = reactive(new Set<string>());
const expandingNodeKeys = reactive(new Set<string>());

const nextNewItem = ref<ControlledListItem>();
const newLabelFormValue = ref("");
const newListFormValue = ref("");
const nextNewList = ref();
const refetcher = ref(0);
const rerenderTree = ref(0);

const { setDisplayedRow } = inject<{ setDisplayedRow: RowSetter }>(
    displayedRowKey,
)!;

const route = useRoute();

// Tree is derived from the store. The store owns the canonical
// ControlledList/ControlledListItem data; we project that into TreeNodes
// for PrimeVue.
const tree = computed<TreeNode[]>(() =>
    listStore.lists.map((list: ControlledList) =>
        listAsNode(
            list,
            selectedLanguage.value,
            iconLabels,
            listStore.hasLoadedChildren,
        ),
    ),
);

function getSearchableText(node: TreeNode): string {
    if (nodeIsList(node)) {
        return (node.data.name ?? "").toLowerCase();
    }
    const values = (node.data.values ?? []) as Value[];
    return values.map((v) => (v.value ?? "").toLowerCase()).join("\n");
}

const { debouncedFilterValue, filteredTree, isFilterCapped } =
    useCappedTreeFilter(
        tree,
        expandedKeys,
        filterValue,
        FILTER_DEBOUNCE_MS,
        FILTER_RENDER_CAP,
        getSearchableText,
    );

// Hydrate the store the first time the tree mounts so we don't refetch
// across route changes inside the manager.
onMounted(async () => {
    try {
        await listStore.initialize();
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Unable to fetch lists"),
            detail: error instanceof Error ? error.message : undefined,
        });
    }
});

async function onNodeExpand(node: TreeNode) {
    const nodeKey = node.key as string;

    expandingNodeKeys.add(nodeKey);
    requestAnimationFrame(() => {
        setTimeout(() => expandingNodeKeys.delete(nodeKey), 600);
    });

    if (nodeIsList(node)) {
        // Lists ship their root items eagerly; nothing to lazy-load.
        return;
    }
    const itemId = nodeKey;
    if (listStore.hasLoadedChildren(itemId)) {
        return;
    }
    loadingNodeKeys.add(itemId);
    try {
        await listStore.loadChildren(itemId);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Unable to fetch children"),
            detail: error instanceof Error ? error.message : undefined,
        });
    } finally {
        loadingNodeKeys.delete(itemId);
    }
}

const updateSelectedAndExpanded = (node: TreeNode) => {
    if (isMultiSelecting.value || movingItem.value?.key) {
        return;
    }
    setDisplayedRow(node.data);

    if (!expandedKeys.value[node.key]) {
        expandingNodeKeys.add(node.key as string);
        requestAnimationFrame(() => {
            setTimeout(() => expandingNodeKeys.delete(node.key as string), 600);
        });
    }

    expandedKeys.value = {
        ...expandedKeys.value,
        [node.key]: true,
    };
};

// Eager-load the affected list whenever the user enters a flow that needs
// the whole subtree (multi-select, item move).
watch(isMultiSelecting, async (active) => {
    if (!active) return;
    const displayedListId = inferListIdFromDisplayedRow();
    if (displayedListId) {
        try {
            await listStore.loadListEagerly(displayedListId);
        } catch (error) {
            toast.add({
                severity: ERROR,
                life: DEFAULT_ERROR_TOAST_LIFE,
                summary: $gettext("Unable to load list for multi-select"),
                detail: error instanceof Error ? error.message : undefined,
            });
        }
    }
});

watch(movingItem, async (next) => {
    if (!next?.data?.list_id) return;
    try {
        await listStore.loadListEagerly(next.data.list_id);
    } catch (error) {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Unable to load list for move"),
            detail: error instanceof Error ? error.message : undefined,
        });
    }
});

function inferListIdFromDisplayedRow(): string | null {
    // The displayed row is provided via injection by the parent. We rely on
    // the selectedKeys reactive to find what's currently being edited
    // because we don't have direct displayedRow access in this scope.
    const firstSelected = Object.keys(selectedKeys.value)[0];
    if (!firstSelected) return null;
    const item = listStore.findItem(firstSelected);
    if (item) return item.list_id;
    const list = listStore.findList(firstSelected);
    return list ? list.id : null;
}

async function revealItemInTree(itemId: string): Promise<TreeNode | null> {
    try {
        const { found } = findNodeInTree(tree.value, itemId);
        if (found) return found;
    } catch {
        // not in memory yet; fall through to ancestor load
    }
    try {
        await listStore.loadAncestorPath(itemId);
        const { found } = findNodeInTree(tree.value, itemId);
        return found ?? null;
    } catch {
        return null;
    }
}

async function navigate(newRoute: RouteLocationNormalizedLoadedGeneric) {
    switch (newRoute.name) {
        case routeNames.splash:
            setDisplayedRow(null);
            expandedKeys.value = {};
            selectedKeys.value = {};
            break;
        case routeNames.list: {
            if (!tree.value.length) return;
            const list = tree.value.find(
                (node) => node.data.id === newRoute.params.id,
            );
            if (list) {
                setDisplayedRow(list.data);
                expandedKeys.value = {
                    ...expandedKeys.value,
                    [list.data.id]: true,
                };
                selectedKeys.value = { [list.data.id]: true };
            } else {
                setDisplayedRow(null);
            }
            break;
        }
        case routeNames.item: {
            if (!tree.value.length) return;
            const itemId = newRoute.params.id as string;
            const found = await revealItemInTree(itemId);
            if (found) {
                setDisplayedRow(found.data);
                // Collect ancestor ids so we can expand them all at once.
                let ancestorId = (found.data as ControlledListItem).parent_id;
                const idsToExpand: string[] = [
                    (found.data as ControlledListItem).list_id,
                ];
                while (ancestorId) {
                    idsToExpand.push(ancestorId);
                    const ancestor = listStore.findItem(ancestorId);
                    ancestorId = ancestor?.parent_id ?? null;
                }
                expandedKeys.value = {
                    ...expandedKeys.value,
                    ...Object.fromEntries(idsToExpand.map((id) => [id, true])),
                };
                selectedKeys.value = { [found.data.id]: true };
            } else {
                toast.add({
                    severity: ERROR,
                    life: DEFAULT_ERROR_TOAST_LIFE,
                    summary: $gettext(`List Item ${itemId} not found`),
                });
                setDisplayedRow(null);
            }
            break;
        }
    }
}

// React to route changes.
watch(
    [
        () => {
            return { ...route };
        },
    ],
    ([newRoute]) => {
        navigate(newRoute);
    },
);

// Navigate on initial population of the tree.
watch(
    () => tree.value.length,
    (length) => {
        if (length > 0) {
            navigate(route);
        }
    },
);

// When the filter doesn't match anything in the loaded shallow
// tree, hit FilteredListView per visible list, then lazy-load the
// returned branches so the capped filter re-evaluates.
let serverFilterAbortToken = 0;
watch(debouncedFilterValue, async (next) => {
    if (!next || filteredTree.value.length > 0 || isFilterCapped.value) {
        return;
    }
    const token = ++serverFilterAbortToken;
    for (const list of listStore.lists) {
        if (token !== serverFilterAbortToken) return;
        try {
            const data = await fetchFilteredList(list.id, next);
            const items = (data.items ?? []) as Array<{
                id: string;
                parent_ids?: string[];
            }>;
            const parentIdsToLoad = new Set<string>();
            for (const item of items) {
                for (const pid of item.parent_ids ?? []) {
                    parentIdsToLoad.add(pid);
                }
            }
            // Load ancestors sequentially so a parent loads before its child
            // (each load may surface new ids that need expanding).
            for (const pid of parentIdsToLoad) {
                if (token !== serverFilterAbortToken) return;
                if (!listStore.hasLoadedChildren(pid)) {
                    try {
                        await listStore.loadChildren(pid);
                    } catch {
                        /* surface via toast only if all loads fail */
                    }
                }
            }
        } catch (error) {
            // One list failing shouldn't block searches in other lists.
            console.warn(
                `Server-side search of list ${list.id} failed:`,
                error,
            );
        }
    }
});
</script>

<template>
    <ListTreeControls
        :key="refetcher"
        v-model:rerender-tree="rerenderTree"
        v-model:expanded-keys="expandedKeys"
        v-model:selected-keys="selectedKeys"
        v-model:moving-item="movingItem"
        v-model:is-multi-selecting="isMultiSelecting"
        v-model:should-copy-children="shouldCopyChildren"
        v-model:next-new-list="nextNewList"
        v-model:new-list-form-value="newListFormValue"
        :tree="tree"
    />
    <div class="filter-container">
        <InputText
            v-model="filterValue"
            class="tree-filter-input"
            type="text"
            :placeholder="FILTER_PLACEHOLDER"
            :aria-label="FILTER_PLACEHOLDER"
        />
        <Message
            v-if="isFilterCapped"
            severity="warn"
            :closable="false"
            class="filter-cap-message"
        >
            {{ FILTER_CAPPED_MESSAGE }}
        </Message>
    </div>
    <Tree
        v-if="filteredTree"
        :key="rerenderTree"
        v-model:selection-keys="selectedKeys"
        v-model:expanded-keys="expandedKeys"
        :value="filteredTree"
        :selection-mode="isMultiSelecting ? 'checkbox' : 'single'"
        :pt="{
            root: {
                style: {
                    flexGrow: 1,
                    overflowY: 'hidden',
                    paddingBottom: '5rem',
                    paddingRight: '0rem',
                },
            },
            wrapper: {
                style: {
                    overflowY: 'auto',
                    maxHeight: '100%',
                    paddingBottom: '1rem',
                },
            },
            container: { style: { fontSize: '1.4rem' } },
            nodeContent: ({ instance }: TreePassThroughMethodOptions) => {
                if (instance.$el && instance.node.key === movingItem?.key) {
                    instance.$el.classList.add('is-adjusting-parent');
                }
                return { style: { height: '4rem' } };
            },
            nodeIcon: ({ instance }: TreePassThroughMethodOptions) => {
                return { ariaLabel: instance.node.iconLabel };
            },
            nodeLabel: {
                style: {
                    textWrap: 'nowrap',
                    marginLeft: '0.5rem',
                    width: '100%',
                },
            },
            nodeToggleButton: ({ instance }: TreePassThroughMethodOptions) => ({
                class: {
                    'node-children-loading':
                        loadingNodeKeys.has(instance.node?.key as string) ||
                        expandingNodeKeys.has(instance.node?.key as string),
                },
            }),
        }"
        @node-select="updateSelectedAndExpanded"
        @node-expand="onNodeExpand"
    >
        <template #default="slotProps">
            <TreeRow
                v-model:expanded-keys="expandedKeys"
                v-model:selected-keys="selectedKeys"
                v-model:moving-item="movingItem"
                v-model:refetcher="refetcher"
                v-model:rerender-tree="rerenderTree"
                v-model:next-new-item="nextNewItem"
                v-model:new-label-form-value="newLabelFormValue"
                v-model:new-list-form-value="newListFormValue"
                v-model:filter-value="filterValue"
                :tree="tree"
                :icon-labels
                :move-labels
                :node="slotProps.node"
                :is-multi-selecting="isMultiSelecting"
                :should-copy-children="shouldCopyChildren"
            />
        </template>
    </Tree>
</template>

<style scoped>
:deep(.is-adjusting-parent) {
    border: dashed;
}

.filter-container {
    padding: 0.5rem 1rem;
    background: var(--p-content-hover-background);
    border-bottom: 1px solid var(--p-content-border-color);
}

.tree-filter-input {
    width: 100%;
    height: 3.5rem;
    font-size: 1.4rem;
    border-radius: 2px;
}

.filter-cap-message {
    margin-top: 0.5rem;
    font-size: 1.2rem;
}

:deep(.p-tree-node) {
    margin-inline-end: 0.5rem;
}

/* Ensure smooth chevron rotation on expand/collapse */
:deep(.p-tree-node-toggle-button .p-tree-node-toggle-icon) {
    transition: transform 0.2s ease-in-out;
}

/* Spin the expand toggle icon while children are being fetched. */
:deep(.node-children-loading .p-tree-node-toggle-icon) {
    animation: tree-toggle-spin 0.6s linear infinite;
    pointer-events: none;
}

@keyframes tree-toggle-spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}
</style>
