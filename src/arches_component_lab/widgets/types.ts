import {
    CONFIGURE,
    EDIT,
    VIEW,
} from "@/arches_component_lab/widgets/constants";

export type WidgetMode = typeof CONFIGURE | typeof EDIT | typeof VIEW;

export interface URLDatatype {
    url: string;
    url_label: string;
}
