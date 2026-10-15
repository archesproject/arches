import type {
    LayerDefinition,
    MapLayer,
    OverlaySwatch,
} from "@/arches_vue_components/components/MapComponent/types.ts";

const SECONDARY_LAYER_ID_PATTERN = /halo|hover|click|cluster/;
const COLOR_STRING_PATTERN = /^(#|rgba?\(|hsla?\()/;

const COLOR_PAINT_PROPERTY_BY_LAYER_TYPE: Record<
    string,
    { property: string; kind: "fill" | "line" | "point" }
> = {
    fill: { property: "fill-color", kind: "fill" },
    line: { property: "line-color", kind: "line" },
    circle: { property: "circle-color", kind: "point" },
};

function isColorLiteral(value: unknown): value is string {
    return typeof value === "string";
}

function collectColorLiterals(expression: unknown): string[] {
    if (isColorLiteral(expression)) {
        return COLOR_STRING_PATTERN.test(expression) ? [expression] : [];
    }
    if (Array.isArray(expression)) {
        return expression.flatMap(collectColorLiterals);
    }
    return [];
}

function deriveGradientSwatch(
    layerDefinition: LayerDefinition,
): OverlaySwatch | null {
    const colors = collectColorLiterals(
        layerDefinition.paint?.["heatmap-color"],
    );
    if (colors.length < 2) {
        return null;
    }
    return { kind: "gradient", colors };
}

export function deriveOverlaySwatch(overlay: MapLayer): OverlaySwatch | null {
    const primaryLayerDefinitions = overlay.layerdefinitions.filter(
        (layerDefinition) =>
            !SECONDARY_LAYER_ID_PATTERN.test(layerDefinition.id),
    );

    for (const layerDefinition of primaryLayerDefinitions) {
        if (layerDefinition.type === "heatmap") {
            const gradientSwatch = deriveGradientSwatch(layerDefinition);
            if (gradientSwatch) {
                return gradientSwatch;
            }
        }

        const colorProperty =
            COLOR_PAINT_PROPERTY_BY_LAYER_TYPE[layerDefinition.type];
        if (!colorProperty) {
            continue;
        }

        const color = layerDefinition.paint?.[colorProperty.property];
        if (isColorLiteral(color)) {
            return { kind: colorProperty.kind, color };
        }
    }

    if (overlay.icon) {
        return { kind: "icon", iconClass: overlay.icon };
    }
    return null;
}
