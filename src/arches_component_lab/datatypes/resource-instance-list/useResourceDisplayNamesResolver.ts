import { ref, watch } from "vue";

import { useResourceDisplayNameStore } from "@/arches_component_lab/stores/useResourceDisplayNameStore.ts";

import type { Ref } from "vue";
import type {
    ResourceInstanceReference,
    ResourceInstanceListOption,
} from "@/arches_component_lab/datatypes/resource-instance-list/types.ts";

export function useResourceDisplayNamesResolver(
    nodeValue: Ref<ResourceInstanceReference[] | null>,
    graphSlug: string,
    nodeAlias: string,
) {
    const resolved = ref<ResourceInstanceListOption[]>([]);
    const loading = ref(false);
    let latestRequestId = 0;

    watch(
        nodeValue,
        async (newNodeValue) => {
            const requestId = ++latestRequestId;
            resolved.value = [];
            const resourceInstanceIds =
                newNodeValue
                    ?.map((resourceReference) => resourceReference.resourceId)
                    .filter(Boolean) ?? [];
            loading.value = resourceInstanceIds.length > 0;
            if (!resourceInstanceIds.length) {
                loading.value = false;
                return;
            }

            const result =
                await useResourceDisplayNameStore().fetchDisplayNames(
                    graphSlug,
                    nodeAlias,
                    resourceInstanceIds,
                );
            if (requestId === latestRequestId) {
                resolved.value = result;
                loading.value = false;
            }
        },
        { immediate: true },
    );

    return { resolved, loading };
}
