import arches from "arches";
import Cookies from "js-cookie";

export const postDisplayedListToServer = async (displayedList, toast, $gettext) => {
    try {
        const response = await fetch(
            arches.urls.controlled_list(displayedList.id),
            {
                method: "POST",
                headers: {
                    "X-CSRFToken": Cookies.get("csrftoken"),
                },
                body: JSON.stringify(displayedList),
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
