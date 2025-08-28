import type {
    CollectionItem,
    ConceptValue,
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

export function convertConceptOptionToFormValue(
    conceptOption: Record<string, boolean> | string | null,
    options: CollectionItem[],
): ConceptValue {
    let conceptOptionId: string | null = null;
    if (
        typeof conceptOption === "string" ||
        typeof conceptOption === "undefined"
    ) {
        conceptOptionId = conceptOption;
    } else {
        conceptOptionId = Object.keys(
            conceptOption as Record<string, boolean>,
        )?.[0];
    }

    if (!conceptOptionId) return blankConceptValue();
    const option = getOption(conceptOptionId, options);

    return {
        display_value: option ? (option as CollectionItem).label : "",
        node_value: option?.key ?? null,
        details: option ? [option] : [],
    };
}

/**
 * Flatten a tree of CollectionItem objects into a single array.
 *
 * @param items - The hierarchical list.
 * @returns A flat array of all items (with empty children arrays).
 */
export function flattenCollectionItems(
    items: CollectionItem[],
): CollectionItem[] {
    const result: CollectionItem[] = [];

    function recurse(nodes: CollectionItem[]): void {
        for (const node of nodes) {
            // Push a copy without the original children
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

export function blankConceptValue() {
    return {
        display_value: "",
        node_value: null,
        details: [],
    };
}
