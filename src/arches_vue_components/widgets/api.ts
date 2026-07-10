import arches from "arches";

export async function fetchLanguages() {
    const response = await fetch(
        arches.urls.api_languages_with_request_language,
    );
    const parsed = await response.json();
    if (!response.ok) throw new Error(parsed.message || response.statusText);
    return parsed;
}
