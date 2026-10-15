import { generateArchesURL } from "@/arches_vue_components/application/generate-arches-url.ts";

export const fetchRelatableResources = async (
    graphSlug: string,
    nodeAlias: string,
    page: number,
    filterTerm?: string[] | string,
    initialValue?: string | null | undefined,
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

    if (initialValue) {
        params.append("initialValue", initialValue);
    }

    const url = generateArchesURL(
        "arches_vue_components:api-relatable-resources",
        {
            graph: graphSlug,
            node_alias: nodeAlias,
        },
    );
    const response = await fetch(`${url}?${params}`);

    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message || response.statusText);
    return parsed;
};
