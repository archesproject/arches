import { computed, ref, watch } from "vue";

import { useConceptTreeStore } from "@/arches_component_lab/stores/useConceptTreeStore.ts";
import { getOption } from "@/arches_component_lab/datatypes/concept/utils.ts";

import type { Ref } from "vue";
import type { CollectionItem } from "@/arches_component_lab/datatypes/concept/types.ts";

export function useConceptLabelResolver(
    nodeValue: Ref<string | null>,
    graphSlug: string,
    nodeAlias: string,
) {
    const resolved = ref<CollectionItem | null>(null);
    const loading = ref(false);
    let latestRequestId = 0;

    watch(
        nodeValue,
        async (newConceptId) => {
            const requestId = ++latestRequestId;
            resolved.value = null;
            loading.value = !!newConceptId;
            if (!newConceptId) {
                loading.value = false;
                return;
            }
            if (!graphSlug || !nodeAlias) {
                loading.value = false;
                return;
            }
            const conceptTree = await useConceptTreeStore().fetchTree(
                graphSlug,
                nodeAlias,
            );
            if (requestId === latestRequestId) {
                resolved.value = getOption(newConceptId, conceptTree.results);
                loading.value = false;
            }
        },
        { immediate: true },
    );

    const label = computed(() => resolved.value?.label ?? null);
    return { resolved, label, loading };
}
