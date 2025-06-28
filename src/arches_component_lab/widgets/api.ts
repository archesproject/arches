import arches from "arches";

import type { ResourceInstanceReference } from "@/arches_component_lab/widgets/types.ts";

export const fetchCardXNodeXWidgetData = async (
    graphSlug: string,
    nodeAlias: string,
) => {
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
};

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

export const fetchRelatableResources = async (
    graphSlug: string,
    nodeAlias: string,
    page: number,
    filterTerm?: string,
    initialValues?: ResourceInstanceReference[] | null | undefined,
) => {
    const params = new URLSearchParams();

    params.append("page", page.toString());
    if (filterTerm) {
        params.append("filter_term", filterTerm);
    }
    initialValues?.forEach((initialValue) =>
        params.append("initialValue", initialValue.resource_id),
    );
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
