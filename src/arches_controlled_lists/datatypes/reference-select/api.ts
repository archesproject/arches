import arches from "arches";

export const fetchWidgetOptions = async (
    graphSlug: string,
    nodeAlias: string,
) => {
    const params = new URLSearchParams();
    params.append("graph_slug", graphSlug);
    params.append("node_alias", nodeAlias);
    const response = await fetch(
        `${arches.urls.controlled_list_options}?${params}`,
    );
    try {
        const parsed = await response.json();
        if (response.ok) {
            return parsed;
        }
        throw new Error(parsed.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};
