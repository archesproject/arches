import {
    CONFIGURE,
    EDIT,
    VIEW,
} from "@/arches_component_lab/widgets/constants.ts";

export type WidgetMode = typeof CONFIGURE | typeof EDIT | typeof VIEW;

export interface BaseWidgetProps {
    mode: WidgetMode;
    nodeAlias?: string;
    graphSlug?: string;
}
