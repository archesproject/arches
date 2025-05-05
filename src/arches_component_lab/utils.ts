import { ALT_LABEL, PREF_LABEL } from "@/arches_component_lab/constants.ts";

import type { Label, Labellable, WithLabels, WithValues } from "@/arches_component_lab/types";


/* Port of rank_label in arches.app.utils.i18n python module */
export const rankLabel = (
    label: Label,
    preferredLanguageCode: string,
    systemLanguageCode: string,
): number => {
    let rank = 1;
    if (label.valuetype_id === PREF_LABEL) {
        rank = 10;
    } else if (label.valuetype_id === ALT_LABEL) {
        rank = 4;
    }

    // Some arches deployments may not have standardized capitalizations.
    const labelLanguageFull = label.language_id.toLowerCase();
    const labelLanguageNoRegion = label.language_id
        .split(/[-_]/)[0]
        .toLowerCase();
    const preferredLanguageFull = preferredLanguageCode.toLowerCase();
    const preferredLanguageNoRegion = preferredLanguageCode
        .split(/[-_]/)[0]
        .toLowerCase();
    const systemLanguageFull = systemLanguageCode.toLowerCase();
    const systemLanguageNoRegion = systemLanguageCode
        .split(/[-_]/)[0]
        .toLowerCase();

    if (labelLanguageFull === preferredLanguageFull) {
        rank *= 10;
    } else if (labelLanguageNoRegion === preferredLanguageNoRegion) {
        rank *= 5;
    } else if (labelLanguageFull === systemLanguageFull) {
        rank *= 3;
    } else if (labelLanguageNoRegion === systemLanguageNoRegion) {
        rank *= 2;
    }

    return rank;
};

export const getItemLabel = (
    item: Labellable,
    preferredLanguageCode: string,
    systemLanguageCode: string,
): Label => {
    const labels = (item as WithLabels).labels ?? (item as WithValues).values;
    if (!labels.length) {
        return {
            value: "",
            language_id: "",
            valuetype_id: "",
        };
    }
    return labels.sort(
        (a, b) =>
            rankLabel(b, preferredLanguageCode, systemLanguageCode) -
            rankLabel(a, preferredLanguageCode, systemLanguageCode),
    )[0];
};
