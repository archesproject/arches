import arches from "arches";

// TODO: Remove when full replacement of fetchCardXNodeXWidgetData is implemented
export const fetchWidgetData = async (graphSlug: string, nodeAlias: string) => {
    const response = await fetch(
        arches.urls.api_widget_data(graphSlug, nodeAlias),
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

// TODO: Remove when full replacement of fetchCardXNodeXWidgetData is implemented
export const fetchNodeData = async (graphSlug: string, nodeAlias: string) => {
    const response = await fetch(
        arches.urls.api_node_data(graphSlug, nodeAlias),
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

export const fetchCardXNodeXWidgetDataFromNodeGroup = async (
    graphSlug: string,
    nodegroupAlias: string,
) => {
    const response = await fetch(
        arches.urls.api_card_x_node_x_widget_list_from_nodegroup(
            graphSlug,
            nodegroupAlias,
        ),
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
