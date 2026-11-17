<script setup lang="ts">
import { computed, useId } from "vue";

import { useGettext } from "vue3-gettext";

import Select from "openvue/select";

import SettingsToggleRow from "@/arches_vue_components/components/MapComponent/components/SettingsPanel/components/SettingsToggleRow.vue";

import { useResolvedMapContext } from "@/arches_vue_components/components/MapComponent/composables/useMapContext.ts";
import { isGeographicCoordinateSystem } from "@/arches_vue_components/components/MapComponent/utils/coordinate-systems.ts";

import type { MapContext } from "@/arches_vue_components/components/MapComponent/types.ts";

const { context = undefined } = defineProps<{
    context?: MapContext;
}>();

const { settings, coordinateSystems } = useResolvedMapContext(
    context,
    "SettingsPanel",
);

const { $gettext } = useGettext();

const readoutSridSelectId = useId();
const readoutFormatSelectId = useId();
const scaleUnitSelectId = useId();

const coordinateFormatOptions = [
    { label: $gettext("Decimal degrees"), value: "dd" },
    { label: $gettext("Degrees, minutes, seconds"), value: "dms" },
];

const scaleUnitOptions = [
    { label: $gettext("Metric (km / m)"), value: "metric" },
    { label: $gettext("Imperial (mi / ft)"), value: "imperial" },
];

const coordinateSystemOptions = computed(() =>
    coordinateSystems.value.map((coordinateSystem) => ({
        label: coordinateSystem.name,
        value: coordinateSystem.srid,
    })),
);

const isReadoutGeographic = computed(() => {
    const readoutCoordinateSystem = coordinateSystems.value.find(
        (coordinateSystem) =>
            coordinateSystem.srid === settings.value.coordinateReadoutSrid,
    );
    return (
        !readoutCoordinateSystem ||
        isGeographicCoordinateSystem(readoutCoordinateSystem)
    );
});
</script>

<template>
    <section class="settings-section">
        <h3 class="settings-section-header">{{ $gettext("Status bar") }}</h3>
        <SettingsToggleRow
            v-model="settings.showCursorCoordinates"
            :label="$gettext('Show cursor coordinates')"
        />
        <div
            v-if="settings.showCursorCoordinates"
            class="settings-suboption"
        >
            <label
                class="settings-suboption-label"
                :for="readoutSridSelectId"
            >
                {{ $gettext("Coordinate system") }}
            </label>
            <Select
                v-model="settings.coordinateReadoutSrid"
                option-label="label"
                option-value="value"
                append-to="self"
                size="small"
                :input-id="readoutSridSelectId"
                :options="coordinateSystemOptions"
                :fluid="true"
            />
            <template v-if="isReadoutGeographic">
                <label
                    class="settings-suboption-label"
                    :for="readoutFormatSelectId"
                >
                    {{ $gettext("Format") }}
                </label>
                <Select
                    v-model="settings.coordinateReadoutFormat"
                    option-label="label"
                    option-value="value"
                    append-to="self"
                    size="small"
                    :input-id="readoutFormatSelectId"
                    :options="coordinateFormatOptions"
                    :fluid="true"
                />
            </template>
        </div>
        <SettingsToggleRow
            v-model="settings.showMapScale"
            :label="$gettext('Show map scale')"
        />
        <div
            v-if="settings.showMapScale"
            class="settings-suboption"
        >
            <label
                class="settings-suboption-label"
                :for="scaleUnitSelectId"
            >
                {{ $gettext("Units") }}
            </label>
            <Select
                v-model="settings.mapScaleUnit"
                option-label="label"
                option-value="value"
                append-to="self"
                size="small"
                :input-id="scaleUnitSelectId"
                :options="scaleUnitOptions"
                :fluid="true"
            />
        </div>
        <SettingsToggleRow
            v-model="settings.showZoomLevel"
            :label="$gettext('Show zoom level')"
        />
    </section>

    <section class="settings-section">
        <h3 class="settings-section-header">{{ $gettext("Search") }}</h3>
        <SettingsToggleRow
            v-model="settings.geocoderVisible"
            :label="$gettext('Show place search')"
            :description="
                $gettext(
                    'The search box in the top-right corner of the map, for finding a place by name.',
                )
            "
        />
    </section>

    <section class="settings-section">
        <h3 class="settings-section-header">{{ $gettext("Map behavior") }}</h3>
        <SettingsToggleRow
            v-model="settings.scrollZoomRequiresKey"
            :label="$gettext('Require Ctrl/Cmd + scroll to zoom')"
            :description="
                $gettext(
                    'When on, scrolling over the map with a plain mouse wheel scrolls the page instead of zooming the map — hold Ctrl (or ⌘ on Mac) while scrolling to zoom.',
                )
            "
        />
        <p class="settings-footnote">
            {{
                $gettext(
                    "Starts from this map's default configuration — changing it here only affects your current session.",
                )
            }}
        </p>
    </section>

    <section class="settings-section">
        <h3 class="settings-section-header">{{ $gettext("Camera") }}</h3>
        <SettingsToggleRow
            v-model="settings.allow3d"
            :label="$gettext('Allow 3D (tilt & rotate)')"
            :description="
                $gettext(
                    'When off, the map stays flat and north-up — drag-to-tilt and drag-to-rotate are disabled, and any existing tilt/rotation resets.',
                )
            "
        />
    </section>
</template>

<style scoped>
.settings-section {
    display: flex;
    flex-direction: column;
    gap: 1.1rem;
    padding-block: 1.45rem;
    padding-inline: 1.6rem;
}

.settings-section + .settings-section {
    border-block-start: 0.1rem solid var(--p-content-border-color);
}

.settings-section-header {
    margin: 0;
    color: var(--p-text-muted-color);
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.06rem;
    text-transform: uppercase;
}

.settings-footnote {
    margin: 0;
    color: var(--p-text-muted-color);
    font-size: 1.15rem;
    line-height: 1.4;
}

.settings-suboption {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding-inline-start: 1.1rem;
    border-inline-start: 0.2rem solid var(--p-content-border-color);
}

.settings-suboption-label {
    margin: 0;
    color: var(--p-text-muted-color);
    font-size: 1.15rem;
    font-weight: 600;
}
</style>
