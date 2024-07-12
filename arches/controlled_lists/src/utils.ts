import arches from "arches";

import type { TreeNode } from "primevue/treenode";
import type { Language } from "@/arches/types";
import type {
    ControlledList,
    ControlledListItem,
    Selectable,
} from "@/controlled-lists/types";

// Duck-typing helpers
export const dataIsList = (data: Selectable) => {
    return (data as ControlledList).search_only !== undefined;
};
export const dataIsItem = (data: Selectable) => {
    return !dataIsList(data);
};
export const nodeIsItem = (node: TreeNode) => {
    return !nodeIsList(node);
};
export const nodeIsList = (node: TreeNode) => {
    return dataIsList(node.data);
};

export const bestLabel = (item: ControlledListItem, languageCode: string) => {
    const valuesInLang = item.values.filter(
        (value) => value.language_id === languageCode,
    );
    const bestLabel =
        valuesInLang.find((value) => value.valuetype_id === "prefLabel") ??
        valuesInLang.find((value) => value.valuetype_id === "altLabel") ??
        item.values.find((value) => value.valuetype_id === "prefLabel");
    if (!bestLabel) {
        throw new Error();
    }
    return bestLabel;
};

export const languageNameFromCode = (code: string) => {
    return arches.languages.find((lang: Language) => lang.code === code).name;
};

export const findNodeInTree = (tree: TreeNode[], itemId: string) => {
    function recurse(items: TreeNode[]): TreeNode | undefined {
        for (const item of items) {
            if (item.data.id === itemId) {
                return item;
            }
            for (const child of item.items ?? item.children) {
                const maybeFound = recurse([child]);
                if (maybeFound) {
                    return maybeFound;
                }
            }
        }
    }

    return recurse(tree);
};

export const itemAsNode = (
    item: ControlledListItem,
    selectedLanguage: Language,
): TreeNode => {
    return {
        key: item.id,
        children: item.children.map((child) =>
            itemAsNode(child, selectedLanguage),
        ),
        data: item,
    };
};

export const listAsNode = (
    list: ControlledList,
    selectedLanguage: Language,
): TreeNode => {
    return {
        key: list.id,
        children: list.items.map((item: ControlledListItem) =>
            itemAsNode(item, selectedLanguage),
        ),
        data: list,
    };
};

export const makeParentMap = (list: ControlledList) => {
    const map = {};

    const stripAllButParentRecursive = (
        items: ControlledListItem[],
        acc: { [key: string]: string | null },
    ) => {
        for (const item of items) {
            acc[item.id] = item.parent_id;
            stripAllButParentRecursive(item.children, acc);
        }
    };

    stripAllButParentRecursive(list.items, map);
    return map;
};

export const makeSortOrderMap = (list: ControlledList) => {
    const map = {};

    const stripAllButSortOrderRecursive = (
        items: ControlledListItem[],
        acc: { [key: string]: number },
    ) => {
        for (const item of items) {
            acc[item.id] = item.sortorder;
            stripAllButSortOrderRecursive(item.children, acc);
        }
    };

    stripAllButSortOrderRecursive(list.items, map);
    return map;
};

export const reorderItems = (
    list: ControlledList,
    item: ControlledListItem,
    siblings: ControlledListItem[],
    up: boolean,
) => {
    /* This isn't child's play because sort order is "flat", whereas
    reordering involves moving hierarchy subsets.

    With this tree:
        1
        |- 2
        |- 3
        4
        5

    Moving the first item "down" one should result in:
        1
        2
        |- 3
        |- 4
        5

        (1 -> 4)
        (2 -> 1)
        (3 -> 2)
        (4 -> 3)
        (5 -> 5)

    We're going to accomplish this by reordering the moved item among
    its immediate siblings, and then recalculating sort order through the
    entire list. The python view will just care that the sortorder
    value is correct, not that the items actually present in that order
    in the JSON data, but we're still going to reorder the JSON so we can
    use it to update client state if the server returns an empty success msg.
    */

    const indexInSiblings = siblings.indexOf(item);
    const itemsToLeft = siblings.slice(0, indexInSiblings);
    const itemsToRight = siblings.slice(indexInSiblings + 1);

    let reorderedSiblings: ControlledListItem[];
    let patchSiblings = true;
    if (up) {
        const leftNeighbor = itemsToLeft.pop();
        if (!leftNeighbor) {
            // Cannot shift upward - already at top
            throw new Error();
        }
        reorderedSiblings = [
            ...itemsToLeft,
            item,
            leftNeighbor,
            ...itemsToRight,
        ];
    } else {
        const [rightNeighbor, ...rest] = itemsToRight;
        if (!rightNeighbor) {
            // Already at bottom. Might end up here from a "move" operation
            // that added the new item to the end.
            reorderedSiblings = [...itemsToLeft, item];
            patchSiblings = false;
        } else {
            reorderedSiblings = [...itemsToLeft, rightNeighbor, item, ...rest];
        }
    }

    let acc = 0;
    const recalculateSortOrderRecursive = (
        parent: Selectable,
        items: ControlledListItem[],
    ) => {
        // Patch in the reordered siblings.
        if (
            patchSiblings &&
            items.some((itemCandidate) => itemCandidate.id === item.id)
        ) {
            if ((parent as ControlledList).items) {
                (parent as ControlledList).items = reorderedSiblings;
            } else {
                (parent as ControlledListItem).children = reorderedSiblings;
            }
            items = reorderedSiblings;
        }
        for (const thisItem of items) {
            thisItem.sortorder = acc;
            acc += 1;
            recalculateSortOrderRecursive(thisItem, thisItem.children);
        }
    };

    recalculateSortOrderRecursive(list, list.items);
};

export const vFocus = {
    /*
    The editor (pencil) button from the DataTable hogs focus with a
    setTimeout of 1, so we'll queue behind it to set focus to the input.
    This should be reported/clarified with PrimeVue with a MWE.
    */
    mounted: (el: HTMLInputElement) => {
        // @ts-expect-error focusVisible not yet in typeshed
        setTimeout(() => el && el.focus({ focusVisible: true }), 5);
    },
    updated: (el: HTMLInputElement) => {
        // @ts-expect-error focusVisible not yet in typeshed
        setTimeout(() => el && el.focus({ focusVisible: true }), 5);
    },
};
