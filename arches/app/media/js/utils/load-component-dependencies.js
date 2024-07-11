/* eslint-disable */

define([], function() {
    return function loadComponentDependencies(componentPaths){
        for (const componentPath of componentPaths) {
            try {  // first try to load project path
                require(`${APP_ROOT_DIRECTORY}/media/js/${componentPath}`);
            }
            catch(e) {  // if project path fails, look in applications
                try {
                    if (ARCHES_APPLICATIONS.length === 0) {  // ensures fallthrough to Arches-core
                        throw new Error();
                    }
                    for (const archesApp of ARCHES_APPLICATIONS) {
                        try {
                            require(`${SITE_PACKAGES_DIRECTORY}/${archesApp}/media/js/${componentPath}`);
                            break;
                        }
                        catch(e) { // handles egg/wheel links, cannot access them programatically hence manual access
                            try {
                                require(`${LINKED_APPLICATION_PATH_0}/media/js/${componentPath}`);
                                break;
                            }
                            catch {  // handles egg/wheel links, cannot access them programatically hence manual access
                                try {
                                    require(`${LINKED_APPLICATION_PATH_1}/media/js/${componentPath}`);
                                    break;
                                }
                                catch { // handles egg/wheel links, cannot access them programatically hence manual access
                                    try {
                                        require(`${LINKED_APPLICATION_PATH_2}/media/js/${componentPath}`);
                                        break;
                                    }
                                    catch { throw new Error(); } // if all attempts fail within the loop, throw error for outer try/catch
                                }
                            }
                        }
                    }
                }
                catch(e) {  // finally, look in Arches core for component
                    require(`${ARCHES_CORE_DIRECTORY}/app/media/js/${componentPath}`);
                }
            }
        }
    };
});
