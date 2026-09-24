import { onUnmounted, ref, watch } from "vue";

import type { ComputedRef, Ref } from "vue";
import type { TreeExpandedKeys } from "primevue/tree";
import type { TreeNode } from "primevue/treenode";

export function useCappedTreeFilter(
    tree: Ref<TreeNode[]> | ComputedRef<TreeNode[]>,
    expandedKeys: Ref<TreeExpandedKeys>,
    filterValue: Ref<string>,
    filterDebounceMs: number,
    filterRenderCap: number,
    getSearchableText: (treeNode: TreeNode) => string,
) {
    const debouncedFilterValue = ref("");
    const filteredTree = ref<TreeNode[]>([]);
    const isFilterCapped = ref(false);
    const expandedKeysSnapshotBeforeFilter = ref<TreeExpandedKeys>({});

    let filterDebounceTimeoutId: ReturnType<typeof setTimeout> | null = null;

    watch(
        filterValue,
        (nextFilterValue, previousFilterValue) => {
            if (filterDebounceTimeoutId) {
                clearTimeout(filterDebounceTimeoutId);
                filterDebounceTimeoutId = null;
            }

            if (!nextFilterValue) {
                debouncedFilterValue.value = "";
                return;
            }

            if (previousFilterValue === undefined) {
                debouncedFilterValue.value = nextFilterValue;
                return;
            }

            filterDebounceTimeoutId = setTimeout(() => {
                debouncedFilterValue.value = nextFilterValue;
            }, filterDebounceMs);
        },
        { immediate: true },
    );

    watch(
        [tree, debouncedFilterValue],
        ([nextTreeValue, nextDebouncedFilterValue], previousWatchedValue) => {
            const previousFilterValue =
                (previousWatchedValue?.[1] as string | undefined) ?? "";

            const normalizedFilterValue = nextDebouncedFilterValue
                .trim()
                .toLowerCase();
            const normalizedPreviousFilterValue = previousFilterValue
                .trim()
                .toLowerCase();

            const hadFilter = normalizedPreviousFilterValue.length > 0;
            const hasFilter = normalizedFilterValue.length > 0;

            if (!hadFilter && hasFilter) {
                expandedKeysSnapshotBeforeFilter.value = {
                    ...expandedKeys.value,
                };
            }

            if (hadFilter && !hasFilter) {
                expandedKeys.value = {
                    ...expandedKeysSnapshotBeforeFilter.value,
                };
                expandedKeysSnapshotBeforeFilter.value = {};
                isFilterCapped.value = false;
                filteredTree.value = nextTreeValue;
                return;
            }

            if (!hasFilter) {
                isFilterCapped.value = false;
                filteredTree.value = nextTreeValue;
                return;
            }

            const expandedKeysForFilter: TreeExpandedKeys = {};
            const filteredRootNodes: TreeNode[] = [];

            let includedNodeTotal = 0;
            let exceedsCap = false;

            const includeNodeOrCap = () => {
                includedNodeTotal += 1;
                if (includedNodeTotal > filterRenderCap) {
                    exceedsCap = true;
                }
            };

            const filterNode = (treeNode: TreeNode): TreeNode | null => {
                if (exceedsCap) {
                    return null;
                }

                const filteredChildren: TreeNode[] = [];

                for (const childNode of treeNode.children ?? []) {
                    const filteredChildNode = filterNode(childNode);

                    if (filteredChildNode) {
                        filteredChildren.push(filteredChildNode);
                    }

                    if (exceedsCap) {
                        break;
                    }
                }

                if (exceedsCap) {
                    return null;
                }

                const currentNodeMatches = getSearchableText(treeNode).includes(
                    normalizedFilterValue,
                );

                if (!currentNodeMatches && !filteredChildren.length) {
                    return null;
                }

                includeNodeOrCap();

                if (exceedsCap) {
                    return null;
                }

                if (filteredChildren.length) {
                    expandedKeysForFilter[treeNode.key] = true;
                }

                return {
                    ...treeNode,
                    children: filteredChildren,
                };
            };

            for (const rootNode of nextTreeValue) {
                const filteredRootNode = filterNode(rootNode);

                if (exceedsCap) {
                    break;
                }

                if (filteredRootNode) {
                    filteredRootNodes.push(filteredRootNode);
                }
            }

            if (exceedsCap) {
                isFilterCapped.value = true;
                filteredTree.value = nextTreeValue;
                expandedKeys.value = {
                    ...expandedKeysSnapshotBeforeFilter.value,
                };
                return;
            }

            isFilterCapped.value = false;
            filteredTree.value = filteredRootNodes;
            expandedKeys.value = expandedKeysForFilter;
        },
        { immediate: true },
    );

    onUnmounted(() => {
        if (filterDebounceTimeoutId) clearTimeout(filterDebounceTimeoutId);
    });

    return {
        debouncedFilterValue,
        filteredTree,
        isFilterCapped,
    };
}
