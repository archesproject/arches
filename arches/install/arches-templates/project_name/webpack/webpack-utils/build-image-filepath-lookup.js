const Path = require('path');
const fs = require('fs');

const _buildImageFilePathLookup = function(publicPath, path, outerAcc, imageDirectoryPath) {
    const outerPath = imageDirectoryPath || path;   // original `path` arg is persisted through recursion

    return fs.readdirSync(path).reduce((acc, name) => {
        if (fs.lstatSync(path + '/' + name).isDirectory() ) {
            return _buildImageFilePathLookup(
                publicPath,
                path + '/' + name, 
                acc, 
                outerPath
            );
        }
        else {
            const subPath = (path + '/' + name).split('/img/')[1];
            const parsedPath = Path.parse(subPath);
            const filename = parsedPath['dir'] ? parsedPath['dir'] + '/' + parsedPath['base'] : parsedPath['base'];

            return { 
                ...acc, 
                [`${publicPath}img/${filename}`]: Path.resolve(__dirname, `${outerPath}/${subPath}`)
            };
        }
    }, outerAcc);
};

const buildImageFilePathLookup = function(publicPath, archesImagePath, projectImagePath) {
    const coreArchesImageFilePathConfiguration = _buildImageFilePathLookup(publicPath, archesImagePath, {});
    const projectImagePathConfiguration = _buildImageFilePathLookup(publicPath, projectImagePath, {});

    return { 
        ...coreArchesImageFilePathConfiguration,
        ...projectImagePathConfiguration 
    };
};

module.exports = { buildImageFilePathLookup };