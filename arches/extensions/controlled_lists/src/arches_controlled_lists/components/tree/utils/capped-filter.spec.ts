import { nextTick, ref } from "vue";
import { describe, expect, it } from "vitest";

import { useCappedTreeFilter } from "@/arches_controlled_lists/components/tree/utils/capped-filter.ts";

import type { TreeExpandedKeys } from "primevue/tree";
import type { TreeNode } from "primevue/treenode";

const FLUSH_DEBOUNCE_MS = 5;

function makeNode(
    key: string,
    label: string,
    children: TreeNode[] = [],
): TreeNode {
    return {
        key,
        data: { id: key, name: label },
        children,
    };
}

function getSearchableText(node: TreeNode): string {
    return (node.data?.name ?? "").toString().toLowerCase();
}

async function waitForDebounce() {
    await new Promise((resolve) => setTimeout(resolve, FLUSH_DEBOUNCE_MS + 10));
    await nextTick();
}

describe("useCappedTreeFilter", () => {
    it("returns matching subtrees and expands their parents", async () => {
        const tree = ref<TreeNode[]>([
            makeNode("root", "Root", [
                makeNode("child-a", "Alpha"),
                makeNode("child-b", "Beta"),
            ]),
        ]);
        const expandedKeys = ref<TreeExpandedKeys>({});
        const filterValue = ref("");

        const { filteredTree, isFilterCapped } = useCappedTreeFilter(
            tree,
            expandedKeys,
            filterValue,
            FLUSH_DEBOUNCE_MS,
            100,
            getSearchableText,
        );

        filterValue.value = "alpha";
        await waitForDebounce();

        expect(isFilterCapped.value).toBe(false);
        expect(filteredTree.value).toHaveLength(1);
        expect(filteredTree.value[0].children).toHaveLength(1);
        expect(filteredTree.value[0].children![0].key).toBe("child-a");
        expect(expandedKeys.value.root).toBe(true);
    });

    it("flags the result as capped when matches exceed the render cap and restores expansion when cleared", async () => {
        const children: TreeNode[] = [];
        for (let i = 0; i < 10; i++) {
            children.push(makeNode(`child-${i}`, `Match ${i}`));
        }
        const tree = ref<TreeNode[]>([makeNode("root", "Container", children)]);
        const expandedKeys = ref<TreeExpandedKeys>({ root: true });
        const filterValue = ref("");

        const { filteredTree, isFilterCapped } = useCappedTreeFilter(
            tree,
            expandedKeys,
            filterValue,
            FLUSH_DEBOUNCE_MS,
            3,
            getSearchableText,
        );

        filterValue.value = "match";
        await waitForDebounce();

        expect(isFilterCapped.value).toBe(true);
        // When capped, the unfiltered tree is shown unchanged.
        expect(filteredTree.value).toBe(tree.value);

        filterValue.value = "";
        await waitForDebounce();

        expect(isFilterCapped.value).toBe(false);
        expect(expandedKeys.value.root).toBe(true);
    });
});
