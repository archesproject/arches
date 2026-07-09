import { computed, ref, watch } from "vue";

import { useResourceDisplayNameStore } from "@/arches_component_lab/stores/useResourceDisplayNameStore.ts";

import type { Ref } from "vue";
import type {
    ResourceInstanceReference,
    ResourceInstanceSelectOption,
} from "@/arches_component_lab/datatypes/resource-instance/types.ts";

export function useResourceDisplayNameResolver(
    nodeValue: Ref<ResourceInstanceReference | null>,
    graphSlug: string,
    nodeAlias: string,
) {
    const resolved = ref<ResourceInstanceSelectOption | null>(null);
    const loading = ref(false);
    let latestRequestId = 0;

    watch(
        nodeValue,
        async (newNodeValue) => {
            const requestId = ++latestRequestId;
            resolved.value = null;
            loading.value = false;

            if (!newNodeValue?.resourceId) return;

            loading.value = true;
            const result = await useResourceDisplayNameStore().fetchDisplayName(
                graphSlug,
                nodeAlias,
                newNodeValue.resourceId,
            );
            if (requestId === latestRequestId) {
                resolved.value = result;
                loading.value = false;
            }
        },
        { immediate: true },
    );

    const displayValue = computed(() => resolved.value?.display_value ?? null);
    const resourceId = computed(() => resolved.value?.resource_id ?? null);

    return { resolved, displayValue, resourceId, loading };
}
