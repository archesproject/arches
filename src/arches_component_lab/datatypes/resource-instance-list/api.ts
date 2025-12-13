import arches from "arches";
import type { ResourceInstanceListOption } from "@/arches_component_lab/datatypes/resource-instance-list/types.ts";

export const fetchRelatableResources = async (
    graphSlug: string,
    nodeAlias: string,
    page: number,
    filterTerm?: string[] | string,
    initialValues?: ResourceInstanceListOption[] | null | undefined,
) => {
    const params = new URLSearchParams();

    params.append("page", page.toString());
    if (filterTerm) {
        if (!Array.isArray(filterTerm)) {
            filterTerm = [filterTerm];
        }
        filterTerm.forEach((term) => {
            params.append("filter_term", term);
        });
    }
    initialValues?.forEach((initialValue) => {
        params.append("initialValue", initialValue.resource_id);
    });
    const response = await fetch(
        `${arches.urls.api_relatable_resources(
            graphSlug,
            nodeAlias,
        )}?${params}`,
    );

    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message || response.statusText);
    return parsed;
};
