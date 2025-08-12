import arches from "arches";

import { ALT_LABEL, PREF_LABEL } from "@/arches_controlled_lists/constants.ts";

import type { TreeNode } from "primevue/treenode";
import type {
    ControlledList,
    ControlledListItem,
    ControlledListItemImageMetadata,
    IconLabels,
    Label,
    Labellable,
    Language,
    Selectable,
    Value,
    WithLabels,
    WithValues,
} from "@/arches_controlled_lists/types";

// Duck-typing helpers
export const dataIsList = (data: Selectable) => {
    return (data as ControlledList).searchable !== undefined;
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
export const dataIsNew = (
    node:
        | Selectable
        | ControlledListItem
        | Value
        | ControlledListItemImageMetadata,
) => {
    // UUID minted by the server will have a `-`.
    return node.id === null || !node.id.includes("-");
};

// Finders
export const languageNameFromCode = (code: string) => {
    return arches.languages.find((lang: Language) => lang.code === code).name;
};

export const findNodeInTree = (
    tree: TreeNode[],
    itemId: string,
): {
    found: TreeNode | undefined;
    path: TreeNode[];
} => {
    const path: TreeNode[] = [];

    function recurse(items: TreeNode[]): TreeNode | undefined {
        for (const item of items) {
            if (item.data.id === itemId) {
                return item;
            }
            for (const child of item.items ?? item.children) {
                const found = recurse([child]);
                if (found) {
                    path.push(item);
                    return found;
                }
            }
        }
    }

    const found = recurse(tree);
    if (!found) {
        throw new Error();
    }

    return { found, path };
};

/* Port of rank_label in arches.app.utils.i18n python module */
export const rankLabel = (
    label: Label,
    preferredLanguageCode: string,
    systemLanguageCode: string,
): number => {
    let rank = 1;
    if (label.valuetype_id === PREF_LABEL) {
        rank = 10;
    } else if (label.valuetype_id === ALT_LABEL) {
        rank = 4;
    }

    // Some arches deployments may not have standardized capitalizations.
    const labelLanguageFull = label.language_id.toLowerCase();
    const labelLanguageNoRegion = label.language_id
        .split(/[-_]/)[0]
        .toLowerCase();
    const preferredLanguageFull = preferredLanguageCode.toLowerCase();
    const preferredLanguageNoRegion = preferredLanguageCode
        .split(/[-_]/)[0]
        .toLowerCase();
    const systemLanguageFull = systemLanguageCode.toLowerCase();
    const systemLanguageNoRegion = systemLanguageCode
        .split(/[-_]/)[0]
        .toLowerCase();

    if (labelLanguageFull === preferredLanguageFull) {
        rank *= 10;
    } else if (labelLanguageNoRegion === preferredLanguageNoRegion) {
        rank *= 5;
    } else if (labelLanguageFull === systemLanguageFull) {
        rank *= 3;
    } else if (labelLanguageNoRegion === systemLanguageNoRegion) {
        rank *= 2;
    }

    return rank;
};

export const getItemLabel = (
    item: Labellable,
    preferredLanguageCode: string,
    systemLanguageCode: string,
): Label => {
    const labels = (item as WithLabels).labels ?? (item as WithValues).values;
    if (!labels.length) {
        return {
            value: "",
            language_id: "",
            valuetype_id: "",
        };
    }
    return labels.sort(
        (a, b) =>
            rankLabel(b, preferredLanguageCode, systemLanguageCode) -
            rankLabel(a, preferredLanguageCode, systemLanguageCode),
    )[0];
};

// Shapers
export const itemAsNode = (
    item: ControlledListItem,
    selectedLanguage: Language,
    iconLabels: IconLabels,
): TreeNode => {
    return {
        key: item.id,
        children: item.children.map((child) =>
            itemAsNode(child, selectedLanguage, iconLabels),
        ),
        data: item,
        icon: "pi pi-tag",
        iconLabel: iconLabels.item,
    };
};

export const listAsNode = (
    list: ControlledList,
    selectedLanguage: Language,
    iconLabels: IconLabels,
): TreeNode => {
    return {
        key: list.id,
        children: list.items.map((item: ControlledListItem) =>
            itemAsNode(item, selectedLanguage, iconLabels),
        ),
        data: list,
        icon: "pi pi-folder",
        iconLabel: iconLabels.list,
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

// Actions
export const reorderItems = (
    list: ControlledList,
    item: ControlledListItem,
    siblings: ControlledListItem[],
    up: boolean,
) => {
    /* Recalculate sort order through the entire list after a move operation.
    The python view will just care that the sortorder
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

    function recalculateSortOrderRecursive(
        parent: Selectable,
        items: ControlledListItem[],
    ) {
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
        // Renumber siblings starting at 0.
        items.forEach((thisItem, i) => {
            thisItem.sortorder = i;
            recalculateSortOrderRecursive(thisItem, thisItem.children);
        });
    }

    recalculateSortOrderRecursive(list, list.items);
};

export const commandeerFocusFromDataTable = (element: HTMLElement) => {
    /*
    The editor (pencil) button from the DataTable hogs focus with a
    setTimeout of 1, so we'll queue behind it to set focus to the input.
    This should be reported/clarified with PrimeVue with a MWE.
    */
    // @ts-expect-error focusVisible not yet in typeshed
    setTimeout(() => element && element.focus({ focusVisible: true }), 10);
};

// Directives
export const vFocus = {
    mounted: commandeerFocusFromDataTable,
    updated: commandeerFocusFromDataTable,
};

export const shouldUseContrast = () => {
    // See rationale at abandoned PR:
    // https://github.com/archesproject/arches/pull/11327
    // TODO: get setting from settings API instead
    return Array.from(document.getElementsByTagName("link")).some((el) =>
        el.href.endsWith("accessibility.css"),
    );
};
