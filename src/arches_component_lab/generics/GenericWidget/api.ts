import arches from "arches";

export async function fetchCardXNodeXWidgetData(
    graphSlug: string,
    nodeAlias: string,
) {
    const response = await fetch(
        arches.urls.api_card_x_node_x_widget(graphSlug, nodeAlias),
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
}
