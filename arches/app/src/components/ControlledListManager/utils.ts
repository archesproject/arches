import arches from "arches";

import type { Language } from "@/types/arches";
import type {
    ControlledList,
    ControlledListItem,
} from "@/types/ControlledListManager";
import type { TreeNode } from "primevue/tree/Tree/TreeNode";

export const bestLabel = (item: ControlledListItem, languageCode: string) => {
    const labelsInLang = item.labels.filter(l => l.language_id === languageCode);
    const bestLabel = (
        labelsInLang.find(l => l.valuetype_id === "prefLabel")
        ?? labelsInLang.find(l => l.valuetype_id === "altLabel")
        ?? item.labels.find(l => l.valuetype_id === "prefLabel")
    );
    if (!bestLabel) {
        throw new Error();
    }
    return bestLabel;
};

export const languageName = (code: string) => {
    return arches.languages.find((lang: Language) => lang.code === code).name;
};

export const findNodeInTree = (tree: typeof TreeNode[], itemId: string) => {
    function recurse (items: typeof TreeNode[]) : typeof TreeNode | undefined {
        for (const item of items) {
            if (item.data.id === itemId) {
                return item;
            }
            for (const child of item.children) {
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
): typeof TreeNode => {
    return {
        key: item.id,
        label: bestLabel(item, selectedLanguage.code).value,
        children: item.children.map(child => itemAsNode(child, selectedLanguage)),
        data: item,
    };
};

export const listAsNode = (
    list: ControlledList,
    selectedLanguage: Language,
): typeof TreeNode => {
    return {
        key: list.id,
        label: list.name,
        children: list.items.map(
            (item: ControlledListItem) => itemAsNode(item, selectedLanguage)
        ),
        data: list,
    };
};

export const reorderItem = (
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
    in the JSON data.
    */

    const indexInSiblings = siblings.indexOf(item);
    const itemsToLeft = siblings.slice(0, indexInSiblings);
    const itemsToRight = siblings.slice(indexInSiblings + 1);

    let reorderedSiblings: ControlledListItem[];
    if (up) {
        const leftNeighbor = itemsToLeft.pop();
        if (!leftNeighbor) {  // should be impossible, not localized
            throw new Error('Cannot shift upward - already at top');
        }
        reorderedSiblings = [...itemsToLeft, item, leftNeighbor, ...itemsToRight];
    } else {
        const [rightNeighbor, ...rest] = itemsToRight;
        reorderedSiblings = [...itemsToLeft, rightNeighbor, item, ...rest];
    }

    let acc = 0;
    const recalculateSortOrderRecursive = (items: ControlledListItem[]) => {
        // Patch in the reordered siblings.
        if (items.some(x => x.id === item.id)) {
            items = reorderedSiblings;
        }
        for (const thisItem of items) {
            thisItem.sortorder = acc;
            acc += 1;
            recalculateSortOrderRecursive(thisItem.children);
        }
    };

    recalculateSortOrderRecursive(list.items);
};
