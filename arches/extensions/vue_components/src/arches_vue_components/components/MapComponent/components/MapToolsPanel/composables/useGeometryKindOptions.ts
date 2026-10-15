import { computed } from "vue";

import { useGettext } from "vue3-gettext";

import {
    LINE,
    POINT,
    POLYGON,
} from "@/arches_vue_components/components/MapComponent/constants.ts";

import type { ComputedRef } from "vue";

import type { DrawMode } from "@/arches_vue_components/components/MapComponent/types.ts";

export interface GeometryKindOption {
    value: DrawMode;
    label: string;
    icon: string;
}

export function useGeometryKindOptions(
    allowedGeometryTypes: ComputedRef<string[] | null>,
): ComputedRef<GeometryKindOption[]> {
    const { $gettext } = useGettext();

    return computed(() => {
        const allOptions: GeometryKindOption[] = [
            {
                value: POINT,
                label: $gettext("Point"),
                icon: "pi pi-map-marker",
            },
            { value: LINE, label: $gettext("Line"), icon: "pi pi-minus" },
            { value: POLYGON, label: $gettext("Polygon"), icon: "pi pi-stop" },
        ];

        const allowedTypes = allowedGeometryTypes.value;
        if (!allowedTypes?.length) {
            return allOptions;
        }
        return allOptions.filter((option) =>
            allowedTypes.includes(option.value),
        );
    });
}
