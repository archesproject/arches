define([], function() {
    return function loadComponentDependencies(componentPaths){
        for (const componentPath of componentPaths) {
            try {  // first try to load project path
                // eslint-disable-next-line no-undef
                require(`${APP_ROOT_DIRECTORY}/media/js/${componentPath}`);
            }
            catch(e) {  // if project path fails, load arches-core path
                try { 
                    // eslint-disable-next-line no-undef
                    require(`${ARCHES_CORE_DIRECTORY}/app/media/js/${componentPath}`);
                }
                catch(e) {  // if arches-core path fails, look in each arches application for path
                    // eslint-disable-next-line no-undef
                    for (const archesApp of ARCHES_APPLICATIONS) {
                        // eslint-disable-next-line no-undef
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
                                    catch {}
                                }
                            }
                        }
                    }
                }
            }
        }
    };
});
