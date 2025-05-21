import arches from "arches";

export const fetchCardData = async (
    graphSlug: string,
    nodegroupGroupingNodeAlias: string,
) => {
    const response = await fetch(
        arches.urls.api_card_data(graphSlug, nodegroupGroupingNodeAlias),
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
