import arches from "arches";
import Cookies from "js-cookie";

import type { ControlledList, ControlledListItem } from "@/types/controlledListManager.d";

export const postItemToServer = async (item: ControlledListItem, toast, $gettext) => {
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
            try {
                const body = await response.json();
                throw new Error(body.message);
            } catch {
                throw new Error(response.statusText);
            }
        }
    } catch (error) {
        toast.add({
            severity: "error",
            summary: error || $gettext("Save failed"),
            life: 3000,
        });
    }
};

export const postListToServer = async (list: ControlledList, toast, $gettext) => {
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
            try {
                const body = await response.json();
                throw new Error(body.message);
            } catch {
                throw new Error(response.statusText);
            }
        }
    } catch (error) {
        toast.add({
            severity: "error",
            summary: error || $gettext("Save failed"),
            life: 3000,
        });
    }
};
