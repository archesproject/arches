/* eslint-disable */

define([], function() {
    return function loadComponentDependencies(componentPaths){
        for (const componentPath of componentPaths) {
            try {
                if (!ARCHES_APPLICATIONS.length) {  // assumption os running Arches without a project
                    throw new Error()
                }
                for (const archesApp of ARCHES_APPLICATIONS) {
                    try {
                        require(`${SITE_PACKAGES_DIRECTORY}/${archesApp}/media/js/${componentPath}`);
                        break;
                    }
                    // Handle editable installations (with pip install -e).
                    // Webpack needs string literals, hence arbitrary limit of 9.
                    // https://github.com/archesproject/arches/issues/11274
                    catch(e) {
                        try {
                            require(`${LINKED_APPLICATION_PATH_0}/media/js/${componentPath}`);
                            break;
                        }
                        catch {
                            try {
                                require(`${LINKED_APPLICATION_PATH_1}/media/js/${componentPath}`);
                                break;
                            }
                            catch {
                                try {
                                    require(`${LINKED_APPLICATION_PATH_2}/media/js/${componentPath}`);
                                    break;
                                }
                                catch {
                                    try {
                                        require(`${LINKED_APPLICATION_PATH_3}/media/js/${componentPath}`);
                                        break;
                                    }
                                    catch {
                                        try {
                                            require(`${LINKED_APPLICATION_PATH_4}/media/js/${componentPath}`);
                                            break;
                                        }
                                        catch {
                                            try {
                                                require(`${LINKED_APPLICATION_PATH_5}/media/js/${componentPath}`);
                                                break;
                                            }
                                            catch {
                                                try {
                                                    require(`${LINKED_APPLICATION_PATH_6}/media/js/${componentPath}`);
                                                    break;
                                                }
                                                catch {
                                                    try {
                                                        require(`${LINKED_APPLICATION_PATH_7}/media/js/${componentPath}`);
                                                        break;
                                                    }
                                                    catch {
                                                        try {
                                                            require(`${LINKED_APPLICATION_PATH_8}/media/js/${componentPath}`);
                                                            break;
                                                        }
                                                        catch { throw new Error(); } // if all attempts fail within the loop, throw error for outer try/catch
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            catch(e) {  // finally, look in Arches core for component
                require(`${ARCHES_CORE_DIRECTORY}/app/media/js/${componentPath}`);
            }
        }
    };
});
