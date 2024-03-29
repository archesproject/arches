import type { ControlledListItem } from "@/types/ControlledListManager";
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
