export function generateArchesURL(
    urlName: string,
    urlParameters: Record<string, string | number> = {},
    queryParameters?: Record<string, string | number>,
    languageCode?: string,
): string {
    // @ts-expect-error ARCHES_URLS is defined globally
    const routes = ARCHES_URLS[urlName];

    if (!routes || !Array.isArray(routes)) {
        throw new Error(`Key '${urlName}' not found in JSON object`);
    }

    if (!languageCode) {
        languageCode = document.documentElement.lang;
    }

    const routeParameters = {
        ...urlParameters,
        language_code: languageCode.split("-")[0],
    };

    const routeParameterNames = Object.keys(routeParameters);
    const matchingRoute = routes.find(
        (route: { url: string; params: string[] }) =>
            route.params.every((parameter) =>
                routeParameterNames.includes(parameter),
            ),
    );

    if (!matchingRoute) {
        throw new Error(
            `No matching URL pattern for '${urlName}' with provided parameters ${JSON.stringify(routeParameters)}`,
        );
    }

    let url = matchingRoute.url;
    Object.entries(routeParameters).forEach(([key, value]) => {
        url = url.replace(new RegExp(`{${key}}`, "g"), String(value));
    });

    if (queryParameters && Object.keys(queryParameters).length > 0) {
        const searchParameters = new URLSearchParams();
        Object.entries(queryParameters).forEach(([key, value]) => {
            searchParameters.set(key, String(value));
        });
        url = `${url}?${searchParameters.toString()}`;
    }

    return url;
}
