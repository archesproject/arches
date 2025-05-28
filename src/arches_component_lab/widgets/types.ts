import { EDIT, VIEW } from "@/arches_component_lab/widgets/constants";

export type WidgetMode = typeof EDIT | typeof VIEW;

export interface GraphInfo {
    graphid: string;
    name: string;
}

export interface NewResourceInstance {
    displayValue: string;
    graphId: string;
}

export interface ResourceInstanceReference {
    resourceId: string;
    ontologyProperty: string;
    resourceXresourceId?: string;
    inverseOntologyProperty: string;
    display_value?: string;
}

export interface ResourceInstanceResult {
    resourceinstanceid: string;
    display_value: string;
}

export interface FileReference {
    url: string;
    name: string;
    path: string;
    size: number;
    type: string;
    index: number;
    width: number;
    height: number;
    status: string;
    content: string;
    file_id: string;
    accepted: boolean;
    lastModified: number;
    altText: string;
    attribution: string;
    description: string;
    title: string;
}

export interface URLDatatype {
    url: string;
    url_label: string;
}
