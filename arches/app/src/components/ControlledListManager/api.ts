import arches from "arches";
import Cookies from "js-cookie";

import type {
    ControlledList,
    ControlledListItem,
    Label,
    NewLabel,
} from "@/types/controlledListManager.d";

export const postItemToServer = async (item: ControlledListItem, toast, $gettext) => {
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
        }
    } catch {
        toast.add({
            severity: "error",
            summary: errorText || $gettext("Save failed"),
            life: 3000,
        });
    }
};

export const postListToServer = async (list: ControlledList, toast, $gettext) => {
    let errorText;
    try {
        const response = await fetch(
            arches.urls.controlled_list(list.id),
            {
                method: "POST",
                headers: {
                    "X-CSRFToken": Cookies.get("csrftoken"),
                },
                body: JSON.stringify(list),
            }
        );
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        }
    } catch {
        toast.add({
            severity: "error",
            summary: errorText || $gettext("Save failed"),
            life: 3000,
        });
    }
};

export const createLabel = async (label: NewLabel, toast, $gettext) => {
    let errorText;
    try {
        const response = await fetch(arches.urls.label_add, {
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
            severity: "error",
            summary: errorText || $gettext("Save failed"),
            life: 3000,
        });
    }
};

export const deleteLabel = async (label: Label, toast, $gettext) => {
    let errorText;
    try {
        const response = await fetch(arches.urls.label(label.id), {
            method: "DELETE",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
            },
        });
        if (!response.ok) {
            errorText = response.statusText;
            const body = await response.json();
            errorText = body.message;
            throw new Error();
        }
    } catch {
        toast.add({
            severity: "error",
            summary: errorText || $gettext("Deletion failed"),
            life: 3000,
        });
    }
};
