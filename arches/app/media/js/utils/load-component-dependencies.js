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
                            require(`${ARCHES_APPLICATIONS_DIRECTORY}/${archesApp}/media/js/${componentPath}`);
                        }
                        catch(e) { // handles egg files, cannot access them programatically hence manual access
                            try {
                                require(`${EGG_FILE_PATH_0}/${archesApp}/media/js/${componentPath}`);
                            }
                            catch {  // handles egg files, cannot access them programatically hence manual access
                                try {
                                    require(`${EGG_FILE_PATH_1}/${archesApp}/media/js/${componentPath}`);
                                }
                                catch { // handles egg files, cannot access them programatically hence manual access
                                    try {
                                        require(`${EGG_FILE_PATH_2}/${archesApp}/media/js/${componentPath}`);
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
