import { setActivePinia, createPinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/arches_controlled_lists/api.ts", () => ({
    fetchListItemChildren: vi.fn(),
    fetchListItemAncestorPath: vi.fn(),
    fetchListEagerly: vi.fn(),
    fetchListShallow: vi.fn(),
    fetchListsShallow: vi.fn(),
}));

import {
    fetchListItemAncestorPath,
    fetchListItemChildren,
    fetchListsShallow,
} from "@/arches_controlled_lists/api.ts";
import { useListStore } from "@/arches_controlled_lists/stores/useListStore.ts";

const fetchChildrenMock = fetchListItemChildren as ReturnType<typeof vi.fn>;
const fetchAncestorPathMock = fetchListItemAncestorPath as ReturnType<
    typeof vi.fn
>;
const fetchListsShallowMock = fetchListsShallow as ReturnType<typeof vi.fn>;

function shallowList(id: string, rootItems: Array<Record<string, unknown>>) {
    return {
        id,
        name: `list-${id}`,
        dynamic: false,
        searchable: false,
        nodes: [],
        items: rootItems,
    };
}

function shallowItem(
    id: string,
    list_id: string,
    parent_id: string | null,
    has_children: boolean,
) {
    return {
        id,
        list_id,
        parent_id,
        uri: "",
        sortorder: 0,
        guide: false,
        values: [],
        images: [],
        depth: parent_id ? null : 0,
        has_children,
        children: [],
    };
}

describe("useListStore", () => {
    beforeEach(() => {
        setActivePinia(createPinia());
        fetchChildrenMock.mockReset();
        fetchAncestorPathMock.mockReset();
        fetchListsShallowMock.mockReset();
    });

    it("loadChildren registers shallow children under the parent and dedupes inflight requests", async () => {
        fetchListsShallowMock.mockResolvedValue({
            controlled_lists: [
                shallowList("list-1", [
                    shallowItem("parent-1", "list-1", null, true),
                ]),
            ],
        });

        const store = useListStore();
        await store.initialize();

        let resolveChildren: (v: { children: unknown[] }) => void = () => {};
        fetchChildrenMock.mockReturnValue(
            new Promise((resolve) => {
                resolveChildren = resolve;
            }),
        );

        // Two concurrent loadChildren calls should share one fetch.
        const first = store.loadChildren("parent-1");
        const second = store.loadChildren("parent-1");

        expect(fetchChildrenMock).toHaveBeenCalledTimes(1);

        resolveChildren({
            children: [
                shallowItem("child-a", "list-1", "parent-1", false),
                shallowItem("child-b", "list-1", "parent-1", false),
            ],
        });

        const [firstResult, secondResult] = await Promise.all([first, second]);
        expect(firstResult).toBe(secondResult);
        expect(firstResult).toHaveLength(2);

        const parent = store.findItem("parent-1");
        expect(parent).not.toBeNull();
        expect(parent!.children).toHaveLength(2);
        expect(store.hasLoadedChildren("parent-1")).toBe(true);
    });

    it("loadAncestorPath registers each ancestor and lazy-loads their children", async () => {
        fetchListsShallowMock.mockResolvedValue({
            controlled_lists: [
                shallowList("list-1", [
                    shallowItem("root", "list-1", null, true),
                ]),
            ],
        });

        const store = useListStore();
        await store.initialize();

        fetchAncestorPathMock.mockResolvedValue({
            paths: [
                {
                    searchResults: [
                        { id: "list-1", name: "list-1" },
                        shallowItem("root", "list-1", null, true),
                        shallowItem("mid", "list-1", "root", true),
                        shallowItem("leaf", "list-1", "mid", false),
                    ],
                },
            ],
        });

        // loadChildren is invoked for each intermediate ancestor (root, mid).
        fetchChildrenMock.mockImplementation((parentId: string) =>
            Promise.resolve({
                children: [
                    shallowItem(
                        parentId === "root" ? "mid" : "leaf",
                        "list-1",
                        parentId,
                        parentId === "root",
                    ),
                ],
            }),
        );

        await store.loadAncestorPath("leaf");

        // root and mid were lazy-loaded so the leaf attaches to the canonical tree.
        expect(fetchChildrenMock).toHaveBeenCalledWith("root");
        expect(fetchChildrenMock).toHaveBeenCalledWith("mid");
        expect(store.findItem("leaf")).not.toBeNull();
    });
});
