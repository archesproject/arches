const Path = require('path');
const fs = require('fs');

function buildJavascriptFilepathLookup(path, outerAcc, javascriptDirectoryPath) {
    const outerPath = javascriptDirectoryPath || path;   // original `path` arg is persisted through recursion

    return fs.readdirSync(path).reduce((acc, name) => {
        if (fs.lstatSync(path + '/' + name).isDirectory() ) {
            return buildJavascriptFilepathLookup(
                path + '/' + name, 
                acc, 
                outerPath 
            );
        }
        else {
            const subPath = (path + '/' + name).split('js/')[1];
            const parsedPath = Path.parse(subPath);

            let pathName = parsedPath['name'];
        
            if (parsedPath['dir']) {
                pathName = parsedPath['dir'] + '/' + parsedPath['name'];
            }

            return { 
                ...acc, 
                [pathName]: { 'import': `${outerPath}/${subPath}`, 'filename': `js/[name].js` } 
            };
        }
    }, outerAcc);
};

module.exports = { buildJavascriptFilepathLookup };