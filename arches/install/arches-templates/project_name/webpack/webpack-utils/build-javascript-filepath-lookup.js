const Path = require('path');
const fs = require('fs');

function buildJavascriptFilepathLookup(path, outerAcc, javascriptDirectoryPath) {
    const outerPath = javascriptDirectoryPath || path;   // original `path` arg is persisted through recursion

    return fs.readdirSync(path).reduce((acc, name) => {
        if (fs.lstatSync(Path.join(path, name)).isDirectory() ) {
            return buildJavascriptFilepathLookup(
                Path.join(path, name), 
                acc, 
                outerPath 
            );
        }
        else {
            let subPath = Path.join(path, name).split(/js(.*)/s)[1];  // splits only on first occurance
            subPath = subPath.substring(1);
            const parsedPath = Path.parse(subPath);

            let pathName = parsedPath['name'];
        
            if (parsedPath['dir']) {
                pathName = Path.join(parsedPath['dir'], parsedPath['name']);
            }

            return { 
                ...acc, 
                [pathName]: { 'import': Path.join(outerPath, subPath), 'filename': Path.join('js', '[name].js') } 
            };
        }
    }, outerAcc);
};

module.exports = { buildJavascriptFilepathLookup };