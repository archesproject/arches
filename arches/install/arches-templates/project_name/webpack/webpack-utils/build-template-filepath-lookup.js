const Path = require('path');
const fs = require('fs');

const _buildTemplateFilePathLookup = function(path, outerAcc, templateDirectoryPath) {
    const outerPath = templateDirectoryPath || path;   // original `path` arg is persisted through recursion

    return fs.readdirSync(path).reduce((acc, name) => {
        if (fs.lstatSync(path + '/' + name).isDirectory() ) {
            return _buildTemplateFilePathLookup(
                path + '/' + name, 
                acc, 
                outerPath
            );
        }
        else {
            const subPath = (path + '/' + name).split('/templates/')[1];
            const parsedPath = Path.parse(subPath);
            const filename = parsedPath['dir'] ? parsedPath['dir'] + '/' + parsedPath['base'] : parsedPath['base'];

            return { 
                ...acc, 
                [`templates/${filename}`]: Path.resolve(__dirname, `${outerPath}/${subPath}`)
            };
        }
    }, outerAcc);
};

const buildTemplateFilePathLookup = function(archesTemplatePath, projectTemplatePath) {
    const coreArchesTemplateFilePathConfiguration = _buildTemplateFilePathLookup(archesTemplatePath, {});
    const projectTemplatePathConfiguration = _buildTemplateFilePathLookup(projectTemplatePath, {});

    return { 
        ...coreArchesTemplateFilePathConfiguration,
        ...projectTemplatePathConfiguration 
    };
};

module.exports = { buildTemplateFilePathLookup };