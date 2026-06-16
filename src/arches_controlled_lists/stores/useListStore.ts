import { ref } from "vue";
import { defineStore } from "pinia";

import {
    fetchListEagerly,
    fetchListItemAncestorPath,
    fetchListItemChildren,
    fetchListShallow,
    fetchListsShallow,
} from "@/arches_controlled_lists/api.ts";

import type {
    ControlledList,
    ControlledListItem,
} from "@/arches_controlled_lists/types";

function registerItemRecursive(
    item: ControlledListItem,
    canonical: Map<string, ControlledListItem>,
    loadedChildrenIds: Set<string>,
): ControlledListItem {
    const existing = canonical.get(item.id);
    if (existing) {
        existing.uri = item.uri;
        existing.sortorder = item.sortorder;
        existing.guide = item.guide;
        existing.values = item.values;
        existing.images = item.images;
        existing.parent_id = item.parent_id;
        existing.depth = item.depth;
        existing.has_children =
            item.has_children ?? (item.children ?? []).length > 0;
        existing.children = (item.children ?? []).map((child) =>
            registerItemRecursive(child, canonical, loadedChildrenIds),
        );
        loadedChildrenIds.add(existing.id);
        return existing;
    }

    const normalized: ControlledListItem = {
        ...item,
        children: [],
        has_children: item.has_children ?? (item.children ?? []).length > 0,
    };
    canonical.set(normalized.id, normalized);
    normalized.children = (item.children ?? []).map((child) =>
        registerItemRecursive(child, canonical, loadedChildrenIds),
    );
    loadedChildrenIds.add(normalized.id);
    return normalized;
}

export const useListStore = defineStore("controlled-lists", () => {
    const lists = ref<ControlledList[]>([]);
    const isLoading = ref(false);
    const error = ref<Error | null>(null);

    const itemsById = ref<Map<string, ControlledListItem>>(new Map());
    const loadedChildrenIds = ref<Set<string>>(new Set());
    const eagerLoadedListIds = ref<Set<string>>(new Set());

    const inflightChildFetches = new Map<
        string,
        Promise<ControlledListItem[]>
    >();
    const inflightListFetches = new Map<string, Promise<ControlledList>>();
    let inflightRefresh: Promise<void> | null = null;

    function registerShallowItem(item: ControlledListItem): ControlledListItem {
        const existing = itemsById.value.get(item.id);
        if (existing) {
            existing.uri = item.uri;
            existing.sortorder = item.sortorder;
            existing.guide = item.guide;
            existing.values = item.values;
            existing.images = item.images;
            existing.parent_id = item.parent_id;
            existing.depth = item.depth;
            existing.has_children = item.has_children ?? existing.has_children;
            return existing;
        }
        const normalized: ControlledListItem = {
            ...item,
            children: item.children ?? [],
            has_children: item.has_children ?? false,
        };
        itemsById.value.set(normalized.id, normalized);
        return normalized;
    }

    function ingestShallowList(list: ControlledList): ControlledList {
        const normalizedItems = (list.items ?? []).map(registerShallowItem);
        return {
            ...list,
            items: normalizedItems,
        };
    }

    async function initialize() {
        if (inflightRefresh) return inflightRefresh;
        if (lists.value.length > 0) return;
        return refresh();
    }

    async function refresh() {
        const fetchPromise = (async () => {
            isLoading.value = true;
            error.value = null;
            try {
                const data = await fetchListsShallow();
                const fetched = (data.controlled_lists ??
                    []) as ControlledList[];
                itemsById.value.clear();
                loadedChildrenIds.value.clear();
                eagerLoadedListIds.value.clear();
                lists.value = fetched.map(ingestShallowList);
            } catch (err) {
                error.value =
                    err instanceof Error ? err : new Error(String(err));
                throw err;
            } finally {
                isLoading.value = false;
                inflightRefresh = null;
            }
        })();
        inflightRefresh = fetchPromise;
        return fetchPromise;
    }

    async function loadChildren(itemId: string): Promise<ControlledListItem[]> {
        const existing = itemsById.value.get(itemId);
        if (existing && loadedChildrenIds.value.has(itemId)) {
            return existing.children;
        }
        const inflight = inflightChildFetches.get(itemId);
        if (inflight) {
            return inflight;
        }

        const promise = (async () => {
            const data = await fetchListItemChildren(itemId);
            const fetched = (data.children ?? []) as ControlledListItem[];
            const normalizedChildren = fetched.map(registerShallowItem);
            const parent = itemsById.value.get(itemId);
            if (parent) {
                parent.children = normalizedChildren;
                parent.has_children =
                    parent.has_children || normalizedChildren.length > 0;
                loadedChildrenIds.value.add(itemId);
            }
            inflightChildFetches.delete(itemId);
            return normalizedChildren;
        })();

        inflightChildFetches.set(itemId, promise);
        return promise;
    }

    async function loadListEagerly(
        listId: string,
    ): Promise<ControlledList | null> {
        if (eagerLoadedListIds.value.has(listId)) {
            return findList(listId);
        }
        const inflight = inflightListFetches.get(listId);
        if (inflight) {
            return inflight;
        }

        const promise = (async () => {
            const fetched = (await fetchListEagerly(listId)) as ControlledList;
            const normalizedItems = (fetched.items ?? []).map((item) =>
                registerItemRecursive(
                    item,
                    itemsById.value,
                    loadedChildrenIds.value,
                ),
            );
            const merged: ControlledList = {
                ...fetched,
                items: normalizedItems,
            };
            const index = lists.value.findIndex((l) => l.id === listId);
            if (index >= 0) {
                lists.value.splice(index, 1, merged);
            } else {
                lists.value.push(merged);
            }
            eagerLoadedListIds.value.add(listId);
            inflightListFetches.delete(listId);
            return merged;
        })();

        inflightListFetches.set(listId, promise);
        return promise;
    }

    async function loadListShallow(
        listId: string,
    ): Promise<ControlledList | null> {
        const data = (await fetchListShallow(listId)) as ControlledList;
        const merged = ingestShallowList(data);
        const index = lists.value.findIndex((l) => l.id === listId);
        if (index >= 0) {
            lists.value.splice(index, 1, merged);
        } else {
            lists.value.push(merged);
        }
        return merged;
    }

    async function loadAncestorPath(itemId: string): Promise<void> {
        if (itemsById.value.has(itemId)) {
            return;
        }
        const data = await fetchListItemAncestorPath(itemId);
        const paths = (data.paths ?? []) as Array<{
            searchResults: Array<Record<string, unknown>>;
        }>;
        if (!paths.length) {
            return;
        }
        const searchResults = paths[0].searchResults ?? [];
        if (!searchResults.length) {
            return;
        }

        // First entry is the list dict {id, name}; we expect the list to
        // already exist in `lists` because refresh() loaded all summaries.
        // Items follow in root → target order. Lazy-load each ancestor's
        // children so the target ends up attached to the canonical tree.
        for (let i = 1; i < searchResults.length - 1; i++) {
            const ancestor = searchResults[i] as unknown as ControlledListItem;
            registerShallowItem(ancestor);
            if (!loadedChildrenIds.value.has(ancestor.id)) {
                await loadChildren(ancestor.id);
            }
        }

        // Register the target itself.
        const target = searchResults[
            searchResults.length - 1
        ] as unknown as ControlledListItem;
        if (target?.id) {
            registerShallowItem(target);
        }
    }

    function hasLoadedChildren(itemId: string): boolean {
        return loadedChildrenIds.value.has(itemId);
    }

    function findItem(itemId: string): ControlledListItem | null {
        return itemsById.value.get(itemId) ?? null;
    }

    function findList(listId: string): ControlledList | null {
        return lists.value.find((l) => l.id === listId) ?? null;
    }

    function isListEagerlyLoaded(listId: string): boolean {
        return eagerLoadedListIds.value.has(listId);
    }

    function addListShallow(list: ControlledList) {
        const merged = ingestShallowList(list);
        lists.value.push(merged);
        return merged;
    }

    return {
        lists,
        isLoading,
        error,
        initialize,
        refresh,
        loadChildren,
        loadListEagerly,
        loadListShallow,
        loadAncestorPath,
        hasLoadedChildren,
        findItem,
        findList,
        isListEagerlyLoaded,
        addListShallow,
    };
});
