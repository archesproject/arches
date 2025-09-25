export async function loadComponentDependencies(componentPaths) {
    for (const componentPath of componentPaths) {
        let componentLoaded = false;

        for (const archesApp of ARCHES_APPLICATIONS) {
            try {
                require(`${SITE_PACKAGES_DIRECTORY}/${archesApp}/media/js/${componentPath}`);
                componentLoaded = true;
                break;
            }
            catch (e) {
                try {
                    require(`${LINKED_APPLICATION_PATH_0}/media/js/${componentPath}`);
                    componentLoaded = true;
                    break;
                }
                catch {
                    try {
                        require(`${LINKED_APPLICATION_PATH_1}/media/js/${componentPath}`);
                        componentLoaded = true;
                        break;
                    }
                    catch {
                        try {
                            require(`${LINKED_APPLICATION_PATH_2}/media/js/${componentPath}`);
                            componentLoaded = true;
                            break;
                        }
                        catch {
                            try {
                                require(`${LINKED_APPLICATION_PATH_3}/media/js/${componentPath}`);
                                componentLoaded = true;
                                break;
                            }
                            catch {
                                try {
                                    require(`${LINKED_APPLICATION_PATH_4}/media/js/${componentPath}`);
                                    componentLoaded = true;
                                    break;
                                }
                                catch {
                                    try {
                                        require(`${LINKED_APPLICATION_PATH_5}/media/js/${componentPath}`);
                                        componentLoaded = true;
                                        break;
                                    }
                                    catch {
                                        try {
                                            require(`${LINKED_APPLICATION_PATH_6}/media/js/${componentPath}`);
                                            componentLoaded = true;
                                            break;
                                        }
                                        catch {
                                            try {
                                                require(`${LINKED_APPLICATION_PATH_7}/media/js/${componentPath}`);
                                                componentLoaded = true;
                                                break;
                                            }
                                            catch {
                                                try {
                                                    require(`${LINKED_APPLICATION_PATH_8}/media/js/${componentPath}`);
                                                    componentLoaded = true;
                                                    break;
                                                }
                                                catch {
                                                    // Component not found in linked paths, continue to next archesApp
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

        if (!componentLoaded) { // Finally, look in Arches core for the component
            try {
                require(`${ARCHES_CORE_DIRECTORY}/app/media/js/${componentPath}`);
            }
            catch (e) {
                console.error(`Component "${componentPath}" not found in any application or in Arches core.`);
            }
        }
    }
}
