import arches from "arches";
import Cookies from "js-cookie";

import { DEFAULT_ERROR_TOAST_LIFE, ERROR } from "@/components/ControlledListManager/constants.ts";
import { makeSortOrderMap } from "@/components/ControlledListManager/utils.ts";

import type { ToastServiceMethods } from "primevue/toastservice";
import type {
    ControlledList,
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    Value,
    NewControlledListItemImageMetadata,
    NewOrExistingValue,
} from "@/types/ControlledListManager";

type GetText = (s: string) => string;

function getToken() {
    const token = Cookies.get("csrftoken");
    if (!token) {
        throw new Error("Missing csrftoken");
    }
    return token;
}

export const fetchLists = async (
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    let error;
    let response;
    try {
        response = await fetch(arches.urls.controlled_lists);
        if (response.ok) {
            return await response.json();
        } else {
            error = await response.json();
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Unable to fetch lists"),
            detail: error?.message || response?.statusText,
        });
    }
};

export const createList = async(
    name: string,
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    let error;
    let response;
    try {
        response = await fetch(arches.urls.controlled_list_add, {
            method: "POST",
            headers: { "X-CSRFToken": getToken() },
            body: JSON.stringify({ name }),
        });
        if (response.ok) {
            return await response.json();
        } else {
            error = await response.json();
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: $gettext("List creation failed"),
            detail: error?.message || response?.statusText,
        });
    }
};

export const createItem = async (
    item: ControlledListItem,
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    let error;
    let response;
    try {
        response = await fetch(arches.urls.controlled_list_item_add, {
            method: "POST",
            headers: { "X-CSRFToken": getToken() },
            body: JSON.stringify(item),
        });
        if (response.ok) {
            return await response.json();
        } else {
            error = await response.json();
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: $gettext("Item creation failed"),
            detail: error?.message || response?.statusText,
        });
    }
};

export const patchItem = async(
    item: ControlledListItem,
    toast: ToastServiceMethods,
    $gettext: GetText,
    field: "uri" | "guide",
) => {
    let error;
    let response;
    try {
        response = await fetch(arches.urls.controlled_list_item(item.id), {
            method: "PATCH",
            headers: { "X-CSRFToken": getToken() },
            body: JSON.stringify({ [field]: item[field] }),
        });
        if (response.ok) {
            return true;
        } else {
            error = await response.json();
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: $gettext("Save failed"),
            detail: error?.message || response?.statusText,
        });
    }
};


export const postList = async (
    list: ControlledList,
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    let error;
    let response;
    try {
        response = await fetch(arches.urls.controlled_list(list.id), {
            method: "POST",
            headers: { "X-CSRFToken": getToken() },
            body: JSON.stringify(list),
        });
        if (response.ok) {
            return await response.json();
        } else {
            error = await response.json();
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: $gettext("Save failed"),
            detail: error?.message || response?.statusText,
        });
    }
};

export const patchList = async(
    list: ControlledList,
    toast: ToastServiceMethods,
    $gettext: GetText,
    field: "name" | "sortorder",
) => {
    let error;
    let response;

    let body = {};
    switch (field) {
        case "name":
            body = { name: list.name };
            break;
        case "sortorder":
            body = { sortorder_map: makeSortOrderMap(list) };
            break;
    }

    try {
        response = await fetch(arches.urls.controlled_list(list.id), {
            method: "PATCH",
            headers: { "X-CSRFToken": getToken() },
            body: JSON.stringify(body),
        });
        if (response.ok) {
            return true;
        } else {
            error = await response.json();
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: $gettext("Save failed"),
            detail: error?.message || response?.statusText,
        });
    }
};

export const deleteLists = async (
    listIds: string[],
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    const promises = listIds.map((id) =>
        fetch(arches.urls.controlled_list(id), {
            method: "DELETE",
            headers: { "X-CSRFToken": getToken() },
        })
    );

    let anyDeleted = false;
    try {
        const responses = await Promise.all(promises);
        responses.forEach(async (response) => {
            if (response.ok) {
                anyDeleted = true;
            } else {
                const body = await response.json();
                toast.add({
                    severity: ERROR,
                    life: DEFAULT_ERROR_TOAST_LIFE,
                    summary: $gettext("List deletion failed"),
                    detail: body.message,
                });
            }
        });
    } catch {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("List deletion failed"),
        });
    }
    if (anyDeleted) {
        return true;
    }
};

export const deleteItems = async (
    itemIds: string[],
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    const promises = itemIds.map((id) =>
        fetch(arches.urls.controlled_list_item(id), {
            method: "DELETE",
            headers: { "X-CSRFToken": getToken() },
        })
    );

    let anyDeleted = false;
    try {
        const responses = await Promise.all(promises);
        if (responses.some((resp) => resp.ok)) {
            return true;
        }
        responses.forEach(async (response) => {
            if (response.ok) {
                anyDeleted = true;
            } else {
                const body = await response.json();
                toast.add({
                    severity: ERROR,
                    life: DEFAULT_ERROR_TOAST_LIFE,
                    summary: $gettext("Item deletion failed"),
                    detail: body.message,
                });
            }
        });
    } catch {
        toast.add({
            severity: ERROR,
            life: DEFAULT_ERROR_TOAST_LIFE,
            summary: $gettext("Item deletion failed"),
        });
    }
    if (anyDeleted) {
        return true;
    }
};

export const upsertValue = async (
    value: NewOrExistingValue,
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    let error;
    let response;
    const url = value.id
        ? arches.urls.controlled_list_item_value(value.id)
        : arches.urls.controlled_list_item_value_add;
    try {
        response = await fetch(url, {
            method: "POST",
            headers: { "X-CSRFToken": getToken() },
            body: JSON.stringify(value),
        });
        if (response.ok) {
            return await response.json();
        } else {
            error = await response.json();
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: $gettext("Value save failed"),
            detail: error?.message || response?.statusText,
        });
    }
};

export const deleteValue = async (
    value: Value,
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    let error;
    let response;
    try {
        response = await fetch(
            arches.urls.controlled_list_item_value(value.id),
            {
                method: "DELETE",
                headers: { "X-CSRFToken": getToken() },
            }
        );
        if (response.ok) {
            return true;
        } else {
            error = await response.json();
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: $gettext("Value deletion failed"),
            detail: error?.message || response?.statusText,
        });
    }
};

export const upsertMetadata = async (
    metadata: NewControlledListItemImageMetadata,
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    let error;
    let response;
    const url = metadata.id
        ? arches.urls.controlled_list_item_image_metadata(metadata.id)
        : arches.urls.controlled_list_item_image_metadata_add;
    try {
        response = await fetch(url, {
            method: "POST",
            headers: { "X-CSRFToken": getToken() },
            body: JSON.stringify(metadata),
        });
        if (response.ok) {
            return await response.json();
        } else {
            error = await response.json();
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: $gettext("Metadata save failed"),
            detail: error?.message || response?.statusText,
        });
    }
};

export const deleteMetadata = async (
    metadata: ControlledListItemImageMetadata,
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    let error;
    let response;
    try {
        response = await fetch(
            arches.urls.controlled_list_item_image_metadata(metadata.id),
            {
                method: "DELETE",
                headers: { "X-CSRFToken": getToken() },
            }
        );
        if (response.ok) {
            return true;
        } else {
            error = await response.json();
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: $gettext("Metadata deletion failed"),
            detail: error?.message || response?.statusText,
        });
    }
};

export const deleteImage = async(
    image: ControlledListItemImage,
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    let error;
    let response;
    try {
        response = await fetch(
            arches.urls.controlled_list_item_image(image.id),
            {
                method: "DELETE",
                headers: { "X-CSRFToken": getToken() },
            }
        );
        if (response.ok) {
            return true;
        } else {
            error = await response.json();
            throw new Error();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: $gettext("Image deletion failed"),
            detail: error?.message || response?.statusText,
        });
    }
};
