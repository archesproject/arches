export function generateArchesURL(
    urlName: string,
    urlParams: { [key: string]: string | number } = {},
    languageCode?: string,
) {
    // @ts-expect-error ARCHES_URLS is defined globally
    const routes = ARCHES_URLS[urlName];

    if (!routes || !Array.isArray(routes)) {
        throw new Error(`Key '${urlName}' not found in JSON object`);
    }

    const availableParams = Object.keys(urlParams);
    const candidates = routes.filter(
        (route: { url: string; params: string[] }) => {
            return route.params.every((param) => {
                return availableParams.includes(param);
            });
        },
    );

    if (candidates.length === 0) {
        throw new Error(
            `No matching URL pattern for '${urlName}' with provided parameters ${JSON.stringify(urlParams)}`,
        );
    }

    const exactCandidates = candidates.filter((candidate) => {
        return candidate.params.length === availableParams.length;
    });
    const chosen =
        exactCandidates.length > 0 ? exactCandidates[0] : candidates[0];

    let url = chosen.url;
    if (url.includes("{language_code}")) {
        if (!languageCode) {
            languageCode = document.documentElement.lang;
        }

        languageCode = languageCode.split("-")[0];
        url = url.replace("{language_code}", languageCode);
    }

    Object.entries(urlParams).forEach(([key, value]) => {
        url = url.replace(new RegExp(`{${key}}`, "g"), String(value));
    });

    return url;
}
