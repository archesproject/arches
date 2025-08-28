import type {
    CollectionItem,
    ConceptListValue,
} from "@/arches_component_lab/datatypes/concept-list/types.ts";
import {
    getOption,
    flattenCollectionItems,
} from "@/arches_component_lab/datatypes/concept/utils.ts";

export { flattenCollectionItems };

export function convertSelectionToModelValue(
    conceptOptionIds: string[],
    options: CollectionItem[],
): ConceptListValue {
    if (conceptOptionIds.length == 0) return blankConceptListValue();
    const allSelectedOptions: CollectionItem[] = Object.keys(
        conceptOptionIds,
    ).map((key) => getOption(key, options) as CollectionItem);

    return {
        display_value: allSelectedOptions
            .map((option: CollectionItem) => option.label)
            .join(", "),
        node_value: allSelectedOptions.map(
            (option: CollectionItem) => option.key,
        ),
        details: allSelectedOptions,
    };
}

export function blankConceptListValue(): ConceptListValue {
    return {
        display_value: "",
        node_value: [],
        details: [],
    };
}
