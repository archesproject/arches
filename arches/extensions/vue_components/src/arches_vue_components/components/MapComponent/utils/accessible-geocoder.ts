import MaplibreGeocoder from "@maplibre/maplibre-gl-geocoder";

import type {
    MaplibreGeocoderApi,
    MaplibreGeocoderOptions,
} from "@maplibre/maplibre-gl-geocoder";
import type { Map as MaplibreMap } from "maplibre-gl";

export interface GeocoderMessages {
    searchButtonLabel: string;
    clearButtonLabel: string;
    hint: string;
    searching: string;
    placesFound: (count: number) => string;
    noPlacesFound: string;
    searchFailed: string;
    placeChosen: (placeName: string) => string;
}

/*
 * The plugin only searches on Enter and gives no cue that it does, and it
 * announces nothing to screen readers. This adds a visible Search button, a
 * hint tied to the input, and a polite live region that reports each search.
 * It also swaps the plugin's hover-only clear button for one that shows
 * whenever there is text to clear.
 */
export class AccessibleGeocoder extends MaplibreGeocoder {
    private readonly messages: GeocoderMessages;
    private readonly hintId: string;
    private statusElement: HTMLElement | null = null;
    private clearButton: HTMLButtonElement | null = null;
    private isSearching = false;

    constructor(
        geocoderApi: MaplibreGeocoderApi,
        options: MaplibreGeocoderOptions,
        messages: GeocoderMessages,
        hintId: string,
    ) {
        super(geocoderApi, options);
        this.messages = messages;
        this.hintId = hintId;

        this.on("loading", () => {
            this.isSearching = true;
            this.syncClearButton();
            this.announce(this.messages.searching);
        });
        this.on("results", (results) => {
            this.isSearching = false;
            this.syncClearButton();
            const count = results.features?.length ?? 0;
            this.announce(
                count
                    ? this.messages.placesFound(count)
                    : this.messages.noPlacesFound,
            );
        });
        // Fires after an empty "results" event, so this message wins.
        this.on("error", () => this.announce(this.messages.searchFailed));
        this.on("result", ({ result }) => {
            this.syncClearButton();
            this.announce(this.messages.placeChosen(result.place_name));
        });
        this.on("clear", () => {
            this.syncClearButton();
            this.announce("");
        });
    }

    onAdd(map?: MaplibreMap): HTMLElement {
        const container = super.onAdd(map);
        const input = container.querySelector<HTMLInputElement>(
            ".maplibregl-ctrl-geocoder--input",
        );
        if (!input) {
            return container;
        }

        // The plugin positions its icons against the field, so they move into
        // a wrapper that sits beside the new Search button.
        const field = document.createElement("div");
        field.className = "map-geocoder-field";
        field.append(...container.childNodes);

        // The plugin's clear button only shows on hover; ours shows whenever
        // there is text to clear, and still runs the plugin's clear().
        field.querySelector(".maplibregl-ctrl-geocoder--button")?.remove();

        this.clearButton = document.createElement("button");
        this.clearButton.type = "button";
        this.clearButton.className = "map-geocoder-clear-button";
        this.clearButton.setAttribute(
            "aria-label",
            this.messages.clearButtonLabel,
        );
        const clearIcon = document.createElement("i");
        clearIcon.className = "pi pi-times";
        clearIcon.setAttribute("aria-hidden", "true");
        this.clearButton.append(clearIcon);
        this.clearButton.addEventListener("click", () => this.clear());
        field.append(this.clearButton);
        input.addEventListener("input", () => this.syncClearButton());
        this.syncClearButton();

        // The results list is positioned against its parent, so it moves back
        // to the control to span the field and the Search button.
        const suggestions = field.querySelector(".suggestions-wrapper");

        const searchButton = document.createElement("button");
        searchButton.type = "button";
        searchButton.className = "map-geocoder-search-button";
        searchButton.textContent = this.messages.searchButtonLabel;
        searchButton.addEventListener("click", () => searchFrom(input));

        // Enter on a highlighted suggestion chooses it, but the plugin's own
        // Enter handler then searches again and reopens the list. Capture
        // listeners run first, so this stops that second search.
        input.addEventListener(
            "keydown",
            (event) => {
                if (event.key === "Enter" && hasActiveSuggestion(container)) {
                    event.stopImmediatePropagation();
                }
            },
            { capture: true },
        );

        const hint = document.createElement("span");
        hint.id = this.hintId;
        hint.className = "map-geocoder-visually-hidden";
        hint.textContent = this.messages.hint;
        input.setAttribute("aria-describedby", this.hintId);

        this.statusElement = document.createElement("span");
        this.statusElement.className = "map-geocoder-visually-hidden";
        this.statusElement.setAttribute("role", "status");
        this.statusElement.setAttribute("aria-live", "polite");

        container.classList.add("map-geocoder");
        container.append(field, searchButton, hint, this.statusElement);
        if (suggestions) {
            container.append(suggestions);
        }
        return container;
    }

    onRemove(): this {
        this.statusElement = null;
        this.clearButton = null;
        return super.onRemove();
    }

    private syncClearButton(): void {
        if (this.clearButton) {
            const input =
                this.clearButton.parentElement?.querySelector("input");
            this.clearButton.hidden = this.isSearching || !input?.value;
        }
    }

    private announce(message: string): void {
        if (this.statusElement) {
            this.statusElement.textContent = message;
        }
    }
}

function hasActiveSuggestion(container: HTMLElement): boolean {
    const activeSuggestion = container.querySelector<HTMLElement>(
        ".suggestions > li.active",
    );
    return activeSuggestion !== null && activeSuggestion.offsetParent !== null;
}

// Replays Enter so the button runs exactly the plugin's own search path.
function searchFrom(input: HTMLInputElement): void {
    if (!input.value.trim()) {
        input.focus();
        return;
    }
    input.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Enter", bubbles: true }),
    );
}
