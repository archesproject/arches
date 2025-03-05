import arches from "arches";

export const fetchLists = async (
    nodeAliases: string[] | undefined = undefined,
) => {
    const params = new URLSearchParams();
    nodeAliases?.forEach((alias) => params.append("node_alias", alias));
    const response = await fetch(`${arches.urls.controlled_lists}?${params}`);
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
