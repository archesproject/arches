import arches from "arches";
import type { ResourceInstanceReference } from "@/arches_component_lab/widgets/types.ts";

export const fetchRelatableResources = async (
    graphSlug: string,
    nodeAlias: string,
    page: number,
    filterTerm?: string,
    initialValue?: ResourceInstanceReference | null | undefined,
) => {
    const params = new URLSearchParams();

    params.append("page", page.toString());

    if (filterTerm) {
        params.append("filter_term", filterTerm);
    }

    if (initialValue) {
        params.append("initialValue", initialValue.resource_id);
    }

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
