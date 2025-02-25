import type { Value } from "@/arches_controlled_lists/types.ts";

export type WidgetMode = "edit" | "view";

export interface ReferenceOptionValue {
    uri: string;
    list_item_id: string;
    values: Value[];
    display_value: string;
}
