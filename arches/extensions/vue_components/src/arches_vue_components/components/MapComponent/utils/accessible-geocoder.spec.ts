import { describe, expect, it, vi } from "vitest";

import { searchFrom } from "@/arches_vue_components/components/MapComponent/utils/accessible-geocoder.ts";

describe("searchFrom", () => {
    it("searches with Enter only when there is text to search for", () => {
        const input = document.createElement("input");
        document.body.append(input);
        const onKeydown = vi.fn();
        input.addEventListener("keydown", onKeydown);

        input.value = "  ";
        searchFrom(input);
        expect(onKeydown).not.toHaveBeenCalled();
        expect(document.activeElement).toBe(input);

        input.value = "Cambridge";
        searchFrom(input);
        expect(onKeydown).toHaveBeenCalledOnce();
        expect(onKeydown.mock.calls[0][0].key).toBe("Enter");

        input.remove();
    });
});
