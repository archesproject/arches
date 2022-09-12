const Path = require('path');
const fs = require('fs');

const _buildImageFilePathLookup = function(publicPath, path, outerAcc, imageDirectoryPath) {
    const outerPath = imageDirectoryPath || path;   // original `path` arg is persisted through recursion

    return fs.readdirSync(path).reduce((acc, name) => {
        if (fs.lstatSync(Path.join(path, name)).isDirectory() ) {
            return _buildImageFilePathLookup(
                publicPath,
                Path.join(path, name), 
                acc, 
                outerPath
            );
        }
        else {
            let subPath = Path.join(path, name).split(/img(.*)/s)[1];  // splits only on first occurance
            subPath = subPath.substring(1);
            
            const parsedPath = Path.parse(subPath);
            const filename = parsedPath['dir'] ? Path.join(parsedPath['dir'], parsedPath['base']) : parsedPath['base'];

            return { 
                ...acc, 
                [Path.join(publicPath, 'img', filename)]: Path.resolve(__dirname, Path.join(outerPath, subPath))
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