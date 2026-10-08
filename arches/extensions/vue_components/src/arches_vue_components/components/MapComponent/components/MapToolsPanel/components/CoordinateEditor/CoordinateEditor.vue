<script setup lang="ts">
import {
    computed,
    nextTick,
    onUnmounted,
    ref,
    useId,
    useTemplateRef,
    watch,
} from "vue";

import { useGettext } from "vue3-gettext";

import Button from "openvue/button";
import Message from "openvue/message";
import Select from "openvue/select";
import SelectButton from "openvue/selectbutton";

import GeoJsonTextEditor from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/components/GeoJsonTextEditor.vue";
import VertexTable from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/components/VertexTable.vue";
import ToolButtonGroup from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/ToolButtonGroup.vue";

import {
    GEOMETRY_ICON_BY_TYPE,
    POINT,
} from "@/arches_vue_components/components/MapComponent/constants.ts";
import { useDrawnFeatureLabels } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/composables/useDrawnFeatureLabels.ts";
import { useGeometryKindOptions } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/composables/useGeometryKindOptions.ts";
import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import { useCoordinateEditor } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinateEditor.ts";
import { useCoordinatePreview } from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/composables/useCoordinatePreview.ts";

import type {
    CoordinateEntryKind,
    GeoJsonError,
} from "@/arches_vue_components/components/MapComponent/components/MapToolsPanel/components/CoordinateEditor/types.ts";
import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

const CLOSE_EVENT = "close" as const;
const PREVIEW_DEBOUNCE_MILLISECONDS = 300;
const GEOJSON_APPLY_DEBOUNCE_MILLISECONDS = 200;
const VERTEX_FOCUS_ZOOM = 17;

type DisplayMode = "vertices" | "geojson";

const { context = undefined, editingFeatureId = null } = defineProps<{
    context?: MapContext;
    editingFeatureId?: string | null;
}>();

const emit = defineEmits<{
    (event: typeof CLOSE_EVENT): void;
}>();

const vertexTable =
    useTemplateRef<InstanceType<typeof VertexTable>>("vertexTable");

const { $gettext } = useGettext();

const resolvedContext = useResolvedMapContext(context, "CoordinateEditor");
const {
    map,
    coordinateSystems,
    drawnFeatures,
    allowedGeometryTypes,
    fitToFeatures,
} = resolvedContext;
const kindOptions = useGeometryKindOptions(allowedGeometryTypes);
const labelsByFeatureId = useDrawnFeatureLabels(drawnFeatures);
const defaultKind = kindOptions.value[0]?.value ?? POINT;
const {
    editingFeature,
    kind,
    srid,
    rows,
    errorMessage,
    canUndo,
    decimalPlaces,
    axisLabels,
    minimumVertices,
    previewGeometry,
    setKind,
    setSrid,
    updateRow,
    addRow,
    removeRow,
    beginRowEdit,
    commitRowEdit,
    undo,
    getRowWgs84Position,
    buildGeoJsonText,
    applyGeoJsonText,
    submit,
} = useCoordinateEditor(resolvedContext, editingFeatureId, defaultKind);
const { showPreviewGeometry, showVertexHighlight } = useCoordinatePreview(map);

const sridSelectId = useId();

const displayMode = ref<DisplayMode>("vertices");
const focusedRowIndex = ref<number | null>(null);
const geoJsonText = ref("");
const geoJsonErrors = ref<GeoJsonError[]>([]);

let previewTimer: ReturnType<typeof setTimeout> | undefined;
let geoJsonTimer: ReturnType<typeof setTimeout> | undefined;

const displayModeOptions = [
    { value: "vertices", label: $gettext("Vertices"), icon: "pi pi-list" },
    { value: "geojson", label: $gettext("GeoJSON"), icon: "pi pi-code" },
];

const coordinateSystemOptions = computed(() =>
    coordinateSystems.value.map((coordinateSystem) => ({
        label: coordinateSystem.name,
        value: coordinateSystem.srid,
    })),
);

const editingIconClass = computed(() => {
    if (!editingFeature) {
        return "";
    }
    return GEOMETRY_ICON_BY_TYPE[editingFeature.geometry.type];
});

const focusedRowPosition = computed(() => {
    if (focusedRowIndex.value === null) {
        return null;
    }
    return getRowWgs84Position(focusedRowIndex.value);
});

const canCenter = computed(() => {
    if (displayMode.value === "vertices") {
        return focusedRowPosition.value !== null;
    }
    return previewGeometry.value !== null;
});

const editingFeatureLabel = computed(() => {
    if (editingFeatureId === null) {
        return "";
    }
    return labelsByFeatureId.value[editingFeatureId];
});

const listHeaderLabel = computed(() => {
    if (displayMode.value === "vertices") {
        return $gettext("Vertices");
    }
    return $gettext("GeoJSON");
});

const cancelLabel = computed(() => {
    if (editingFeature) {
        return $gettext("Cancel");
    }
    return $gettext("Done");
});

const submitLabel = computed(() => {
    if (editingFeature) {
        return $gettext("Update geometry");
    }
    return $gettext("Add geometry");
});

watch(previewGeometry, (geometry) => {
    clearTimeout(previewTimer);
    previewTimer = setTimeout(
        () => showPreviewGeometry(geometry),
        PREVIEW_DEBOUNCE_MILLISECONDS,
    );
});

watch(focusedRowPosition, (position) => {
    showVertexHighlight(position);
});

onUnmounted(() => {
    clearTimeout(previewTimer);
    clearTimeout(geoJsonTimer);
});

function selectKind(newKind: CoordinateEntryKind): void {
    setKind(newKind);
    focusedRowIndex.value = null;
}

function setDisplayMode(mode: DisplayMode): void {
    if (mode === "geojson") {
        geoJsonText.value = buildGeoJsonText();
        geoJsonErrors.value = [];
    }
    displayMode.value = mode;
}

function updateGeoJsonText(text: string): void {
    geoJsonText.value = text;
    clearTimeout(geoJsonTimer);
    geoJsonTimer = setTimeout(() => {
        geoJsonErrors.value = applyGeoJsonText(text);
    }, GEOJSON_APPLY_DEBOUNCE_MILLISECONDS);
}

function handleRowFocus(index: number): void {
    focusedRowIndex.value = index;
    beginRowEdit();
}

function handleRowRemove(index: number): void {
    removeRow(index);
    if (focusedRowIndex.value !== null && focusedRowIndex.value >= index) {
        focusedRowIndex.value = null;
    }
}

async function handleAddRow(): Promise<void> {
    const insertedIndex = addRow(focusedRowIndex.value);
    focusedRowIndex.value = insertedIndex;
    await nextTick();
    vertexTable.value?.focusRow(insertedIndex);
}

function flushPendingGeoJsonText(): void {
    clearTimeout(geoJsonTimer);
    geoJsonErrors.value = applyGeoJsonText(geoJsonText.value);
}

function handleUndo(): void {
    clearTimeout(geoJsonTimer);
    undo();
    if (displayMode.value === "geojson") {
        geoJsonText.value = buildGeoJsonText();
        geoJsonErrors.value = [];
    }
}

function centerMap(): void {
    if (displayMode.value === "vertices" && focusedRowPosition.value) {
        const [longitude, latitude] = focusedRowPosition.value;
        map.value?.flyTo({
            center: [longitude, latitude],
            zoom: Math.max(map.value.getZoom(), VERTEX_FOCUS_ZOOM),
        });
        return;
    }
    if (previewGeometry.value) {
        fitToFeatures([
            {
                type: "Feature",
                properties: {},
                geometry: previewGeometry.value,
            },
        ]);
    }
}

function handleSubmit(): void {
    if (displayMode.value === "geojson") {
        flushPendingGeoJsonText();
        if (geoJsonErrors.value.length) {
            return;
        }
    }

    const shouldClose = submit();
    if (shouldClose) {
        emit(CLOSE_EVENT);
        return;
    }
    focusedRowIndex.value = null;
    displayMode.value = "vertices";
    geoJsonErrors.value = [];
}
</script>

<template>
    <div class="coordinate-editor">
        <div class="coordinate-editor-section">
            <template v-if="!editingFeature && displayMode === 'vertices'">
                <span class="coordinate-editor-label">
                    {{ $gettext("Geometry type") }}
                </span>
                <ToolButtonGroup
                    :options="kindOptions"
                    :active-value="kind"
                    @select="selectKind"
                />
            </template>
            <div
                v-if="editingFeature"
                class="coordinate-editor-editing"
            >
                <i
                    aria-hidden="true"
                    :class="editingIconClass"
                />
                <span>
                    {{
                        $gettext("Editing %{label}", {
                            label: editingFeatureLabel,
                        })
                    }}
                </span>
            </div>
            <SelectButton
                class="coordinate-editor-mode-toggle"
                option-label="label"
                option-value="value"
                :model-value="displayMode"
                :options="displayModeOptions"
                :allow-empty="false"
                :aria-label="$gettext('Coordinate display mode')"
                @update:model-value="setDisplayMode"
            >
                <template #option="{ option }">
                    <i
                        aria-hidden="true"
                        :class="option.icon"
                    />
                    <span>{{ option.label }}</span>
                </template>
            </SelectButton>
            <template v-if="displayMode === 'vertices'">
                <label
                    class="coordinate-editor-label"
                    :for="sridSelectId"
                >
                    {{ $gettext("Spatial reference system") }}
                </label>
                <Select
                    option-label="label"
                    option-value="value"
                    append-to="self"
                    size="small"
                    :model-value="srid"
                    :input-id="sridSelectId"
                    :options="coordinateSystemOptions"
                    :fluid="true"
                    @update:model-value="setSrid"
                />
            </template>
        </div>

        <div class="coordinate-editor-section coordinate-editor-scroll-section">
            <div class="coordinate-editor-list-header">
                <span class="coordinate-editor-label">
                    {{ listHeaderLabel }}
                </span>
                <div class="coordinate-editor-list-actions">
                    <Button
                        icon="pi pi-search-plus"
                        size="small"
                        :label="$gettext('Center')"
                        :link="true"
                        :disabled="!canCenter"
                        @click="centerMap"
                    />
                    <Button
                        icon="pi pi-undo"
                        size="small"
                        :label="$gettext('Undo')"
                        :link="true"
                        :disabled="!canUndo"
                        @click="handleUndo"
                    />
                </div>
            </div>
            <template v-if="displayMode === 'vertices'">
                <VertexTable
                    ref="vertexTable"
                    :rows="rows"
                    :axis-labels="axisLabels"
                    :decimal-places="decimalPlaces"
                    :minimum-vertices="minimumVertices"
                    :highlighted-row-index="focusedRowIndex"
                    @update-row="updateRow"
                    @focus-row="handleRowFocus"
                    @blur-row="commitRowEdit"
                    @remove-row="handleRowRemove"
                />
                <Button
                    v-if="kind !== 'point'"
                    class="coordinate-editor-add-vertex"
                    icon="pi pi-plus"
                    size="small"
                    :label="$gettext('Add vertex')"
                    :link="true"
                    @click="handleAddRow"
                />
                <Message
                    v-if="errorMessage"
                    severity="error"
                    size="small"
                    role="alert"
                >
                    {{ errorMessage }}
                </Message>
            </template>
            <GeoJsonTextEditor
                v-else
                :model-value="geoJsonText"
                :errors="geoJsonErrors"
                @update:model-value="updateGeoJsonText"
            />
        </div>

        <div class="coordinate-editor-actions">
            <Button
                size="small"
                :label="cancelLabel"
                :link="true"
                @click="emit(CLOSE_EVENT)"
            />
            <Button
                size="small"
                :label="submitLabel"
                @click="handleSubmit"
            />
        </div>
    </div>
</template>

<style scoped>
.coordinate-editor {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
}

.coordinate-editor-section {
    display: flex;
    flex: 0 0 auto;
    flex-direction: column;
    gap: 0.8rem;
    padding-block: 1.1rem;
    padding-inline: 1.3rem;
    border-block-end: 0.1rem solid var(--p-content-border-color);
}

.coordinate-editor-scroll-section {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    border-block-end: none;
}

.coordinate-editor-label {
    margin: 0;
    color: var(--p-text-muted-color);
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.06rem;
    text-transform: uppercase;
}

.coordinate-editor-editing {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    font-size: 1.35rem;
    font-weight: 600;
}

.coordinate-editor-editing .pi {
    color: var(--p-primary-color);
}

.coordinate-editor-mode-toggle {
    display: flex;
}

.coordinate-editor-mode-toggle :deep(.p-togglebutton) {
    flex: 1;
    gap: 0.5rem;
    font-size: 1.2rem;
}

.coordinate-editor-list-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
}

.coordinate-editor-list-actions {
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.coordinate-editor-add-vertex {
    align-self: flex-start;
}

.coordinate-editor-actions {
    display: flex;
    flex: 0 0 auto;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
    padding-block: 1.1rem;
    padding-inline: 1.3rem;
    border-block-start: 0.1rem solid var(--p-content-border-color);
}
</style>
