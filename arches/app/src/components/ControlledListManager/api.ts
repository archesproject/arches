import arches from "arches";
import Cookies from "js-cookie";

import { ERROR } from "@/components/ControlledListManager/constants.ts";
import { sortOrderMap } from "@/components/ControlledListManager/utils.ts";

import type { ToastServiceMethods } from "primevue/toastservice";
import type {
    ControlledList,
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    Value,
    NewControlledListItemImageMetadata,
    NewValue,
} from "@/types/ControlledListManager";

type GetText = (s: string) => string;

export const postItem = async (
    item: ControlledListItem,
    toast: ToastServiceMethods,
    $gettext: GetText
) => {
    let errorText;
    const token = Cookies.get("csrftoken");
    if (!token) {
        return;
    }
    try {
        const response = await fetch(
            arches.urls.controlled_list_item(item.id),
            {
                method: "POST",
                headers: { "X-CSRFToken": token },
                body: JSON.stringify(item),
            }
        );
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        } else {
            return await response.json();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: errorText || $gettext("Save failed"),
        });
    }
};

export const patchItem = async(
    item: ControlledListItem,
    toast: ToastServiceMethods,
    $gettext: GetText,
    field: "uri",
) => {
    let errorText;
    const token = Cookies.get("csrftoken");
    if (!token) {
        return;
    }
    try {
        const response = await fetch(arches.urls.controlled_list_item(item.id), {
            method: "PATCH",
            headers: { "X-CSRFToken": token },
            body: JSON.stringify({ [field]: item[field] }),
        });
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        } else {
            return true;
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: errorText || $gettext("Save failed"),
        });
    }
};


export const postList = async (
    list: ControlledList,
    toast: ToastServiceMethods,
    $gettext: GetText
) => {
    let errorText;
    const token = Cookies.get("csrftoken");
    if (!token) {
        return;
    }
    try {
        const response = await fetch(arches.urls.controlled_list(list.id), {
            method: "POST",
            headers: { "X-CSRFToken": token },
            body: JSON.stringify(list),
        });
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        } else {
            return await response.json();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: errorText || $gettext("Save failed"),
        });
    }
};

export const patchList = async(
    list: ControlledList,
    toast: ToastServiceMethods,
    $gettext: GetText,
    field: "name" | "sortorder",
) => {
    let errorText;
    const token = Cookies.get("csrftoken");
    if (!token) {
        return;
    }

    let body = {};
    switch (field) {
        case "name":
            body = { name: list.name };
            break;
        case "sortorder":
            body = { sortorder_map: sortOrderMap(list) };
            break;
    }

    try {
        const response = await fetch(arches.urls.controlled_list(list.id), {
            method: "PATCH",
            headers: { "X-CSRFToken": token },
            body: JSON.stringify(body),
        });
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        } else {
            return true;
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: errorText || $gettext("Save failed"),
        });
    }
};

export const upsertValue = async (
    value: NewValue,
    toast: ToastServiceMethods,
    $gettext: GetText
) => {
    let errorText;
    const url = value.id
        ? arches.urls.controlled_list_item_value(value.id)
        : arches.urls.controlled_list_item_value_add;
    const token = Cookies.get("csrftoken");
    if (!token) {
        return;
    }
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "X-CSRFToken": token },
            body: JSON.stringify(value),
        });
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        } else {
            return await response.json();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: errorText || $gettext("Value save failed"),
        });
    }
};

export const deleteValue = async (
    value: Value,
    toast: ToastServiceMethods,
    $gettext: GetText
) => {
    let errorText;
    const token = Cookies.get("csrftoken");
    if (!token) {
        return;
    }
    try {
        const response = await fetch(
            arches.urls.controlled_list_item_value(value.id),
            {
                method: "DELETE",
                headers: { "X-CSRFToken": token },
            }
        );
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        } else {
            return true;
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: errorText || $gettext("Value deletion failed"),
        });
    }
};

export const upsertMetadata = async (
    metadata: NewControlledListItemImageMetadata,
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    let errorText;
    const url = metadata.id
        ? arches.urls.controlled_list_item_image_metadata(metadata.id)
        : arches.urls.controlled_list_item_image_metadata_add;
    const token = Cookies.get("csrftoken");
    if (!token) {
        return;
    }
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "X-CSRFToken": token },
            body: JSON.stringify(metadata),
        });
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        } else {
            return await response.json();
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: errorText || $gettext("Metadata save failed"),
        });
    }
};

export const deleteMetadata = async (
    metadata: ControlledListItemImageMetadata,
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    let errorText;
    const token = Cookies.get("csrftoken");
    if (!token) {
        return;
    }
    try {
        const response = await fetch(
            arches.urls.controlled_list_item_image_metadata(metadata.id),
            {
                method: "DELETE",
                headers: { "X-CSRFToken": token },
            }
        );
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        } else {
            return true;
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: errorText || $gettext("Metadata deletion failed"),
        });
    }
};

export const deleteImage = async(
    image: ControlledListItemImage,
    toast: ToastServiceMethods,
    $gettext: GetText,
) => {
    let errorText;
    const token = Cookies.get("csrftoken");
    if (!token) {
        return;
    }
    try {
        const response = await fetch(
            arches.urls.controlled_list_item_image(image.id),
            {
                method: "DELETE",
                headers: { "X-CSRFToken": token },
            }
        );
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        } else {
            return true;
        }
    } catch {
        toast.add({
            severity: ERROR,
            life: 8000,
            summary: errorText || $gettext("Image deletion failed"),
        });
    }
};
