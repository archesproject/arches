define([], function() {
    return function loadComponentDependencies(componentPaths){
        for (const componentPath of componentPaths) {
            try {  // first try to load project path
                // eslint-disable-next-line no-undef
                require(`${PROJECT_PATH}/media/js/${componentPath}`);
            }
            catch(e) {  // if project path fails, load arches-core path
                // eslint-disable-next-line no-undef
                require(`${ARCHES_CORE_DIRECTORY}/app/media/js/${componentPath}`);
            }
        }
    };
});
