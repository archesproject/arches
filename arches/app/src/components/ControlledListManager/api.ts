import arches from "arches";
import Cookies from "js-cookie";

import type { ToastServiceMethods } from "primevue/toastservice";
import type {
    ControlledList,
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    Label,
    NewControlledListItemImageMetadata,
    NewLabel,
} from "@/types/ControlledListManager";

const ERROR = "error";
type GetText = (s: string) => string;

export const postItemToServer = async (
    item: ControlledListItem,
    toast: ToastServiceMethods,
    $gettext: GetText
) => {
    let errorText;
    try {
        const response = await fetch(
            arches.urls.controlled_list_item(item.id),
            {
                method: "POST",
                headers: {
                    "X-CSRFToken": Cookies.get("csrftoken"),
                },
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
            summary: errorText || $gettext("Save failed"),
        });
    }
};

export const postListToServer = async (
    list: ControlledList,
    toast: ToastServiceMethods,
    $gettext: GetText
) => {
    let errorText;
    try {
        const response = await fetch(arches.urls.controlled_list(list.id), {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
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
            summary: errorText || $gettext("Save failed"),
        });
    }
};

export const upsertLabel = async (
    label: NewLabel,
    toast: ToastServiceMethods,
    $gettext: GetText
) => {
    let errorText;
    const url = label.id
        ? arches.urls.controlled_list_item_label(label.id)
        : arches.urls.controlled_list_item_label_add;
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
            body: JSON.stringify(label),
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
            summary: errorText || $gettext("Label save failed"),
        });
    }
};

export const deleteLabel = async (
    label: Label,
    toast: ToastServiceMethods,
    $gettext: GetText
) => {
    let errorText;
    try {
        const response = await fetch(
            arches.urls.controlled_list_item_label(label.id),
            {
                method: "DELETE",
                headers: {
                    "X-CSRFToken": Cookies.get("csrftoken"),
                },
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
            summary: errorText || $gettext("Label deletion failed"),
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
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
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
    try {
        const response = await fetch(
            arches.urls.controlled_list_item_image_metadata(metadata.id),
            {
                method: "DELETE",
                headers: {
                    "X-CSRFToken": Cookies.get("csrftoken"),
                },
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
    try {
        const response = await fetch(
            arches.urls.controlled_list_item_image(image.id),
            {
                method: "DELETE",
                headers: {
                    "X-CSRFToken": Cookies.get("csrftoken"),
                },
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
            summary: errorText || $gettext("Image deletion failed"),
        });
    }
};
