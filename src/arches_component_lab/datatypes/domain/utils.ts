import type {
    DomainAliasedNodeData,
    DomainListAliasedNodeData,
    DomainOption,
} from "@/arches_component_lab/datatypes/domain/types.ts";

export function buildDomainAliasedNodeData(
    nodeValue: string | null,
    options: DomainOption[],
): DomainAliasedNodeData {
    const option = options.find((opt) => opt.id === nodeValue);
    return {
        node_value: nodeValue,
        display_value: option?.text ?? "",
        details: [],
    };
}

export function buildDomainListAliasedNodeData(
    nodeValues: string[] | null,
    options: DomainOption[],
): DomainListAliasedNodeData {
    const selectedOptions = (nodeValues ?? [])
        .map((id) => options.find((opt) => opt.id === id))
        .filter((opt): opt is DomainOption => opt !== undefined);
    return {
        node_value: nodeValues,
        display_value: selectedOptions.map((opt) => opt.text).join(", "),
        details: [],
    };
}
