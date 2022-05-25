define([
    'jquery',
    'knockout',
    'three'
], function($, ko, THREE) {
    ko.bindingHandlers.threePDB = {
        init: function(element, valueAccessor) {
            var config = ko.unwrap(valueAccessor());
            var animationFrame;

            function getRendererSize(){
                var width = $(element).width();
                var height = window.innerHeight;
                config.camera.aspect = width / height;
                config.camera.updateProjectionMatrix();
                return {'height': height, 'width': width}
            };

            config.renderers.forEach(function(renderer){
                var dimensions = getRendererSize();
                renderer.setSize( dimensions.width, dimensions.height );
                element.append( renderer.domElement );
            });
            
            loadFile(config.displayContent.url);
            
            window.addEventListener( 'resize', onWindowResize, false );
            
            function onWindowResize() {
                var dimensions = getRendererSize();
                config.renderers.forEach(function(renderer){
                    renderer.setSize( dimensions.width, dimensions.height );
                });
                config.controls.handleResize();
            }
    
            function animate() {
                animationFrame = window.requestAnimationFrame( animate );
                config.controls.handleResize();
                config.controls.update();
                var time = Date.now() * 0.0004;
                config.root.rotation.x = time;
                config.root.rotation.y = time * 0.7;
                render();
            }
    
            function render() {      
                config.renderers.forEach(function(renderer){
                    renderer.render( config.scene, config.camera );
                });
            }

            function loadFile(url) {

                while ( config.root.children.length > 0 ) {
                    var object = config.root.children[ 0 ];
                    object.parent.remove( object );
                }

                config.loader.load( url, function( pdb ) {
                    var geometryAtoms = pdb.geometryAtoms;
                    var geometryBonds = pdb.geometryBonds;
                    var json = pdb.json;
                    var boxGeometry = new THREE.BoxBufferGeometry( 1, 1, 1 );
                    var sphereGeometry = new THREE.IcosahedronGeometry( 1, 2 );
                    geometryAtoms.computeBoundingBox();
                    geometryAtoms.boundingBox.getCenter( config.offset ).negate();
                    geometryAtoms.translate( config.offset.x, config.offset.y, config.offset.z );
                    geometryBonds.translate( config.offset.x, config.offset.y, config.offset.z );

                    var positions = geometryAtoms.getAttribute( 'position' );
                    var colors = geometryAtoms.getAttribute( 'color' );

                    var position = new THREE.Vector3();
                    var color = new THREE.Color();

                    for ( var i = 0; i < positions.count; i ++ ) {

                        position.x = positions.getX( i );
                        position.y = positions.getY( i );
                        position.z = positions.getZ( i );

                        color.r = colors.getX( i );
                        color.g = colors.getY( i );
                        color.b = colors.getZ( i );

                        var material = new THREE.MeshPhongMaterial( { color: color } );

                        var object = new THREE.Mesh( sphereGeometry, material );
                        object.position.copy( position );
                        object.position.multiplyScalar( 75 );
                        object.scale.multiplyScalar( 25 );
                        config.root.add( object );

                        var atom = json.atoms[ i ];

                        var text = window.document.createElement( 'div' );
                        text.className = 'label';
                        text.style.color = 'rgb(' + atom[ 3 ][ 0 ] + ',' + atom[ 3 ][ 1 ] + ',' + atom[ 3 ][ 2 ] + ')';
                        text.textContent = atom[ 4 ];

                        var label = new THREE.CSS2DObject( text );
                        label.position.copy( object.position );
                        config.root.add( label );

                    }

                    positions = geometryBonds.getAttribute( 'position' );

                    var start = new THREE.Vector3();
                    var end = new THREE.Vector3();

                    for ( var j = 0; j < positions.count; j += 2 ) {

                        start.x = positions.getX( j );
                        start.y = positions.getY( j );
                        start.z = positions.getZ( j );

                        end.x = positions.getX( j + 1 );
                        end.y = positions.getY( j + 1 );
                        end.z = positions.getZ( j + 1 );

                        start.multiplyScalar( 75 );
                        end.multiplyScalar( 75 );

                        var mesh = new THREE.Mesh( boxGeometry, new THREE.MeshPhongMaterial( 0xffffff ) );
                        mesh.position.copy( start );
                        mesh.position.lerp( end, 0.5 );
                        mesh.scale.set( 5, 5, start.distanceTo( end ) );
                        mesh.lookAt( end );
                        config.root.add( mesh );

                    }

                    render();
                    animate();
                    config.loading(false);
                });

            }

            ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
                window.cancelAnimationFrame(animationFrame);
            }); 
        }

    };

    return ko.bindingHandlers.threePDB;
});
