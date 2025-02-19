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
