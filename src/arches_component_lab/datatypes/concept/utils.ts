import type {
    CollectionItem,
    ConceptAliasedNodeData,
} from "@/arches_component_lab/datatypes/concept/types.ts";

export function getOption(
    value: string,
    options: CollectionItem[],
): CollectionItem | null {
    function findNode(
        tree: CollectionItem[],
        predicate: (object: CollectionItem) => boolean,
    ): CollectionItem | null {
        for (const node of tree) {
            if (predicate(node)) return node;
            if (node.children) {
                const result = findNode(node.children, predicate);
                if (result) return result;
            }
        }
        return null;
    }
    return findNode(
        options as CollectionItem[],
        (option: CollectionItem) => option.key == value,
    );
}

export function buildConceptAliasedNodeData(
    nodeValue: string | null,
    options: CollectionItem[],
): ConceptAliasedNodeData {
    if (!nodeValue) return { node_value: null, display_value: "", details: [] };
    const option = getOption(nodeValue, options);
    return {
        node_value: nodeValue,
        display_value: option?.label ?? "",
        details: option ? [option] : [],
    };
}

export function flattenCollectionItems(
    items: CollectionItem[],
): CollectionItem[] {
    const result: CollectionItem[] = [];

    function recurse(nodes: CollectionItem[]): void {
        for (const node of nodes) {
            const { children, ...rest } = node;
            result.push({ ...rest, children: [] });
            if (children && children.length > 0) {
                recurse(children);
            }
        }
    }

    recurse(items);
    return result;
}
