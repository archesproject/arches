define([], function() {
    return function loadComponentDependencies(componentPaths){
        for (const componentPath of componentPaths) {
            try {  // first try to load project path
                // eslint-disable-next-line no-undef
                require(`${APP_ROOT_DIRECTORY}/media/js/${componentPath}`);
            }
            catch(e) {  // if project path fails, load arches-core path
                // eslint-disable-next-line no-undef

                try {
                    require(`${ARCHES_CORE_DIRECTORY}/app/media/js/${componentPath}`);
                }
                catch(e) {
                    require(`/Users/cbyrd/Projects/ENV/lib/python3.8/site-packages/foo_project/media/js/${componentPath}`)
                }
            }
        }
    };
});
