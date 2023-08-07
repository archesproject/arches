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
                catch(e) {  // if arches-core path fails, look in each installed package for path
                    // eslint-disable-next-line no-undef
                    for (const installedPackage of INSTALLED_PACKAGES) {
                        // eslint-disable-next-line no-undef
                        try {
                            require(`${INSTALLED_PACKAGES_DIRECTORY}/${installedPackage}/media/js/${componentPath}`);
                        }
                        catch(e) { // handles egg files, cannot access them programatically hence manual access
                            // try {
                                require(`${EGG_FILE_PATH_0}/${installedPackage}/media/js/${componentPath}`);
                            // }
                            // catch {  // handles egg files, cannot access them programatically hence manual access
                            //     try {
                            //         require(`${EGG_FILE_PATH_1}/${installedPackage}/media/js/${componentPath}`);
                            //     }
                            //     catch { // handles egg files, cannot access them programatically hence manual access
                            //         try {
                            //             require(`${EGG_FILE_PATH_2}/${installedPackage}/media/js/${componentPath}`);
                            //         }
                            //         catch {}
                            //     }
                            // }
                        }
                    }
                }
            }
        }
    };
});
