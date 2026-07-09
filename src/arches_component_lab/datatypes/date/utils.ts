import dayjs from "dayjs";

import type { DateAliasedNodeData } from "@/arches_component_lab/datatypes/date/types.ts";

export function buildDateAliasedNodeData(
    nodeValue: string | null,
): DateAliasedNodeData {
    return {
        node_value: nodeValue,
        display_value: nodeValue ?? "",
        details: [],
    };
}

export function formatDate(date: Date | null, dateFormat: string): string {
    if (!date) {
        return "";
    }

    if (isNaN(date.getTime())) {
        throw new Error("Invalid date");
    } else {
        return dayjs(date).format(dateFormat);
    }
}
