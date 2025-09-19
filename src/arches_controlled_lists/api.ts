import arches from "arches";
import Cookies from "js-cookie";

import {
    makeParentMap,
    makeSortOrderMap,
} from "@/arches_controlled_lists/utils.ts";

import type {
    ControlledList,
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    NewControlledListItem,
    NewOrExistingControlledListItemImageMetadata,
    NewValue,
    Value,
} from "@/arches_controlled_lists/types";

function getToken() {
    const token = Cookies.get("csrftoken");
    if (!token) {
        throw new Error("Missing csrftoken");
    }
    return token;
}

export const fetchLists = async () => {
    const response = await fetch(arches.urls.controlled_lists);
    try {
        const parsed = await response.json();
        if (response.ok) {
            return parsed;
        }
        throw new Error(parsed.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const createList = async (name: string) => {
    const response = await fetch(arches.urls.controlled_list_add, {
        method: "POST",
        headers: { "X-CSRFToken": getToken() },
        body: JSON.stringify({ name }),
    });
    try {
        const parsed = await response.json();
        if (response.ok) {
            return parsed;
        }
        throw new Error(parsed.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const importList = async (file: File, overwriteOption: string) => {
    const formData = new FormData();
    formData.append("skosfile", file);
    formData.append("overwrite_option", overwriteOption);
    const response = await fetch(arches.urls.controlled_list_add, {
        method: "POST",
        headers: { "X-CSRFToken": getToken() },
        body: formData,
    });
    try {
        const parsed = await response.json();
        if (response.ok) {
            return parsed;
        }
        throw new Error(parsed.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const exportList = async (listIds: string[]) => {
    const response = await fetch(arches.urls.controlled_list_export, {
        method: "POST",
        headers: {
            "X-CSRFToken": getToken(),
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ list_ids: listIds }),
    });
    try {
        if (response.ok) {
            const blob = await response.blob();
            return blob;
        }
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const createItem = async (item: NewControlledListItem) => {
    const response = await fetch(arches.urls.controlled_list_item_add, {
        method: "POST",
        headers: { "X-CSRFToken": getToken() },
        body: JSON.stringify(item),
    });
    try {
        const parsed = await response.json();
        if (response.ok) {
            return parsed;
        }
        throw new Error(parsed.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const patchItem = async (
    item: ControlledListItem,
    field: "uri" | "guide",
) => {
    const response = await fetch(arches.urls.controlled_list_item(item.id), {
        method: "PATCH",
        headers: { "X-CSRFToken": getToken() },
        body: JSON.stringify({ [field]: item[field] }),
    });
    if (response.ok) {
        return true;
    }
    try {
        const error = await response.json();
        throw new Error(error.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const copyItem = async (
    source_id: string,
    target_item_id: string | null,
    target_list_id: string,
    copy_children: boolean,
) => {
    const response = await fetch(
        arches.urls.controlled_list_item_copy(source_id),
        {
            method: "POST",
            headers: { "X-CSRFToken": getToken() },
            body: JSON.stringify({
                target_item_id,
                target_list_id,
                copy_children,
            }),
        },
    );
    if (response.ok) {
        return response.json();
    }
    try {
        const error = await response.json();
        throw new Error(error.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const patchList = async (
    list: ControlledList,
    field: "name" | "sortorder" | "children" | "searchable",
) => {
    let body = {};
    switch (field) {
        case "name":
            body = { name: list.name };
            break;
        case "sortorder":
            body = { sortorder_map: makeSortOrderMap(list) };
            break;
        case "children":
            // Parentage is adjusted on the children themselves.
            body = {
                parent_map: makeParentMap(list),
                sortorder_map: makeSortOrderMap(list),
            };
            break;
        case "searchable":
            body = { searchable: list.searchable };
            break;
    }

    const response = await fetch(arches.urls.controlled_list(list.id), {
        method: "PATCH",
        headers: { "X-CSRFToken": getToken() },
        body: JSON.stringify(body),
    });
    if (response.ok) {
        return true;
    }
    try {
        const error = await response.json();
        throw new Error(error.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const deleteLists = async (listIds: string[]) => {
    const promises = listIds.map((id) =>
        fetch(arches.urls.controlled_list(id), {
            method: "DELETE",
            headers: { "X-CSRFToken": getToken() },
        }),
    );
    const settled = await Promise.allSettled(promises);
    const errors = [];
    for (const fulfilled of settled.filter(
        (prom) => prom.status === "fulfilled",
    )) {
        const resp = fulfilled as PromiseFulfilledResult<Response>;
        if (!resp.value.ok) {
            const error = await resp.value.json();
            errors.push(error.message);
        }
    }
    if (errors.length) {
        throw new Error(errors.join("|"));
    }
    return true;
};

export const deleteItems = async (itemIds: string[]) => {
    const promises = itemIds.map((id) =>
        fetch(arches.urls.controlled_list_item(id), {
            method: "DELETE",
            headers: { "X-CSRFToken": getToken() },
        }),
    );
    const settled = await Promise.allSettled(promises);
    const errors = [];
    for (const fulfilled of settled.filter(
        (prom) => prom.status === "fulfilled",
    )) {
        const resp = fulfilled as PromiseFulfilledResult<Response>;
        if (!resp.value.ok) {
            const error = await resp.value.json();
            errors.push(error.message);
        }
    }
    if (errors.length) {
        throw new Error(errors.join("|"));
    }
    return true;
};

export const upsertValue = async (value: Value | NewValue) => {
    const url = value.id
        ? arches.urls.controlled_list_item_value(value.id)
        : arches.urls.controlled_list_item_value_add;
    const method = value.id ? "PUT" : "POST";
    const response = await fetch(url, {
        method,
        headers: { "X-CSRFToken": getToken() },
        body: JSON.stringify(value),
    });
    try {
        const parsed = await response.json();
        if (response.ok) {
            return parsed;
        }
        throw new Error(parsed.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const deleteValue = async (value: Value) => {
    const response = await fetch(
        arches.urls.controlled_list_item_value(value.id),
        {
            method: "DELETE",
            headers: { "X-CSRFToken": getToken() },
        },
    );
    if (response.ok) {
        return true;
    }
    try {
        const error = await response.json();
        throw new Error(error.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const upsertMetadata = async (
    metadata: NewOrExistingControlledListItemImageMetadata,
) => {
    const url = metadata.id
        ? arches.urls.controlled_list_item_image_metadata(metadata.id)
        : arches.urls.controlled_list_item_image_metadata_add;
    const method = metadata.id ? "PUT" : "POST";
    const response = await fetch(url, {
        method,
        headers: { "X-CSRFToken": getToken() },
        body: JSON.stringify(metadata),
    });
    try {
        const parsed = await response.json();
        if (response.ok) {
            return parsed;
        }
        throw new Error(parsed.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const deleteMetadata = async (
    metadata: ControlledListItemImageMetadata,
) => {
    const response = await fetch(
        arches.urls.controlled_list_item_image_metadata(metadata.id),
        {
            method: "DELETE",
            headers: { "X-CSRFToken": getToken() },
        },
    );
    if (response.ok) {
        return true;
    }
    try {
        const error = await response.json();
        throw new Error(error.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const deleteImage = async (image: ControlledListItemImage) => {
    const response = await fetch(
        arches.urls.controlled_list_item_image(image.id),
        {
            method: "DELETE",
            headers: { "X-CSRFToken": getToken() },
        },
    );
    if (response.ok) {
        return true;
    }
    try {
        const error = await response.json();
        throw new Error(error.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};
