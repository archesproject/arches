import type { CardXNodeXWidget } from "@/arches_component_lab/types.ts";

export interface FileListCardXNodeXWidgetData extends CardXNodeXWidget {
    config: CardXNodeXWidget["config"] & {
        acceptedFiles: string;
        maxFiles: number;
        maxFilesize: number;
        rerender: boolean;
        label: string;
    };
}
