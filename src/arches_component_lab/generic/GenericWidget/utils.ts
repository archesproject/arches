export function getUpdatedComponentPath(
    deprecatedComponentPath: string,
): string {
    const deprecatedComponentToUpdatedComponentPathMap: Record<string, string> =
        {
            "views/components/widgets/text":
                "arches_component_lab/widgets/TextWidget/TextWidget",
            "views/components/widgets/concept-select":
                "arches_component_lab/widgets/ConceptSelectWidget/ConceptSelectWidget",
            "views/components/widgets/datepicker":
                "arches_component_lab/widgets/DatePickerWidget/DatePickerWidget",
            "views/components/widgets/rich-text":
                "arches_component_lab/widgets/RichTextWidget/RichTextWidget",
            "views/components/widgets/radio-boolean":
                "arches_component_lab/widgets/RadioBooleanWidget/RadioBooleanWidget",
            "views/components/widgets/map":
                "arches_component_lab/widgets/MapWidget/MapWidget",
            "views/components/widgets/number":
                "arches_component_lab/widgets/NumberWidget/NumberWidget",
            "views/components/widgets/concept-radio":
                "arches_component_lab/widgets/ConceptRadioWidget/ConceptRadioWidget",
            "views/components/widgets/concept-multiselect":
                "arches_component_lab/widgets/ConceptMultiselectWidget/ConceptMultiselectWidget",
            "views/components/widgets/concept-checkbox":
                "arches_component_lab/widgets/ConceptCheckboxWidget/ConceptCheckboxWidget",
            "views/components/widgets/domain-select":
                "arches_component_lab/widgets/DomainSelectWidget/DomainSelectWidget",
            "views/components/widgets/domain-multiselect":
                "arches_component_lab/widgets/DomainMultiselectWidget/DomainMultiselectWidget",
            "views/components/widgets/domain-radio":
                "arches_component_lab/widgets/DomainRadioWidget/DomainRadioWidget",
            "views/components/widgets/domain-checkbox":
                "arches_component_lab/widgets/DomainCheckboxWidget/DomainCheckboxWidget",
            "views/components/widgets/file":
                "arches_component_lab/widgets/FileListWidget/FileListWidget",
            "views/components/widgets/resource-instance-select":
                "arches_component_lab/widgets/ResourceInstanceSelectWidget/ResourceInstanceSelectWidget",
            "views/components/widgets/non-localized-text":
                "arches_component_lab/widgets/NonLocalizedTextWidget/NonLocalizedTextWidget",
            "views/components/widgets/edtf":
                "arches_component_lab/widgets/EdtfWidget/EdtfWidget",
            "views/components/widgets/urldatatype":
                "arches_component_lab/widgets/URLWidget/URLWidget",
            "views/components/widgets/node-value-select":
                "arches_component_lab/widgets/NodeValueSelectWidget/NodeValueSelectWidget",
            "views/components/widgets/resource-instance-multiselect":
                "arches_component_lab/widgets/ResourceInstanceMultiselectWidget/ResourceInstanceMultiselectWidget",
        };

    const resolvedUpdatedComponentPath: string | undefined =
        deprecatedComponentToUpdatedComponentPathMap[deprecatedComponentPath];

    if (resolvedUpdatedComponentPath === undefined) {
        throw new Error(
            `No updated component path found for deprecated path "${deprecatedComponentPath}".`,
        );
    }

    return resolvedUpdatedComponentPath;
}
