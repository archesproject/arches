export function generateArchesURL(
    urlName: string,
    urlParameters: { [key: string]: string | number } = {},
    languageCode?: string,
) {
    // @ts-expect-error ARCHES_URLS is defined globally
    const routes = ARCHES_URLS[urlName];

    if (!routes || !Array.isArray(routes)) {
        throw new Error(`Key '${urlName}' not found in JSON object`);
    }

    if (!languageCode) {
        languageCode = document.documentElement.lang;
    }

    const primaryLanguageCode = languageCode.split("-")[0];

    urlParameters = {
        ...urlParameters,
        language_code: primaryLanguageCode,
    };

    const urlParameterNames = Object.keys(urlParameters);
    const matchingRoute = routes.find(
        (route: { url: string; params: string[] }) => {
            return route.params.every((parameter) => {
                return urlParameterNames.includes(parameter);
            });
        },
    );

    if (!matchingRoute) {
        throw new Error(
            `No matching URL pattern for '${urlName}' with provided parameters ${JSON.stringify(urlParameters)}`,
        );
    }

    let url = matchingRoute.url;
    Object.entries(urlParameters).forEach(([key, value]) => {
        url = url.replace(new RegExp(`{${key}}`, "g"), String(value));
    });

    return url;
}
