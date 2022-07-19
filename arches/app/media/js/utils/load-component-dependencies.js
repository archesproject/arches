define([], function() {
    return function loadComponentDependencies(componentPaths){
        for (componentPath of componentPaths) {
            try {  // first try to load project path
                require(`${PROJECT_PATH}/media/js/${componentPath}`);
            }
            catch(e) {  // if project path fails, load arches-core path
                require(`${ARCHES_CORE_DIRECTORY}/app/media/js/${componentPath}`);
            }
        }
    };
});
