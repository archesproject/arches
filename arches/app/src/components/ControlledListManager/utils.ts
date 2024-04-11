import type { Language } from "@/types/arches";
import type {
    ControlledList,
    ControlledListItem,
} from "@/types/ControlledListManager";
import type { TreeNode } from "primevue/tree/Tree";

export const bestLabel = (item: ControlledListItem, languageCode: string) => {
    const labelsInLang = item.labels.filter(l => l.language === languageCode);
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

export const findItemInTree = (tree: typeof TreeNode[], itemId: string) => {
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
