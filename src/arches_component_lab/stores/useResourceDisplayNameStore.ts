import { defineStore } from "pinia";

import { fetchRelatableResources as fetchSingleRelatableResource } from "@/arches_component_lab/datatypes/resource-instance/api.ts";
import { fetchRelatableResources as fetchListRelatableResources } from "@/arches_component_lab/datatypes/resource-instance-list/api.ts";

import type { ResourceInstanceSelectOption } from "@/arches_component_lab/datatypes/resource-instance/types.ts";
import type { ResourceInstanceListOption } from "@/arches_component_lab/datatypes/resource-instance-list/types.ts";

export const useResourceDisplayNameStore = defineStore(
    "arches_component_lab:resourceDisplayName",
    () => {
        const singleCache = new Map<
            string,
            Promise<ResourceInstanceSelectOption | null>
        >();
        const listCache = new Map<
            string,
            Promise<ResourceInstanceListOption[]>
        >();

        function fetchDisplayName(
            graphSlug: string,
            nodeAlias: string,
            resourceId: string,
        ): Promise<ResourceInstanceSelectOption | null> {
            const key = `${graphSlug}:${nodeAlias}:${resourceId}`;

            if (!singleCache.has(key)) {
                const fetchRequest = fetchSingleRelatableResource(
                    graphSlug,
                    nodeAlias,
                    1,
                    undefined,
                    resourceId,
                ).then((data) => {
                    const item = (
                        data.data as {
                            resourceinstanceid: string;
                            display_value: string;
                        }[]
                    ).find(
                        (resourceRecord) =>
                            resourceRecord.resourceinstanceid === resourceId,
                    );
                    return item
                        ? {
                              resource_id: resourceId,
                              display_value: item.display_value,
                          }
                        : null;
                });
                fetchRequest.catch(() => singleCache.delete(key));
                singleCache.set(key, fetchRequest);
            }
            return singleCache.get(key)!;
        }

        function fetchDisplayNames(
            graphSlug: string,
            nodeAlias: string,
            resourceInstanceIds: string[],
        ): Promise<ResourceInstanceListOption[]> {
            const key = `${graphSlug}:${nodeAlias}:${[...resourceInstanceIds].sort().join(",")}`;

            if (!listCache.has(key)) {
                const fetchRequest = fetchListRelatableResources(
                    graphSlug,
                    nodeAlias,
                    1,
                    undefined,
                    resourceInstanceIds,
                ).then((data) =>
                    (
                        data.data as {
                            resourceinstanceid: string;
                            display_value: string;
                        }[]
                    ).map((resourceRecord) => ({
                        resource_id: resourceRecord.resourceinstanceid,
                        display_value: resourceRecord.display_value,
                    })),
                );
                fetchRequest.catch(() => listCache.delete(key));
                listCache.set(key, fetchRequest);
            }
            return listCache.get(key)!;
        }

        return { fetchDisplayName, fetchDisplayNames };
    },
);
