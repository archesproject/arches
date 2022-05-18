define(['jquery',
    'knockout',
    'three',
    'PCDLoader',
    'TrackballControls',
    'bindings/threePCD'
], function($, ko, THREE) {
    return ko.components.register('pcdreader', {
        viewModel: function(params) {
            this.params = params;
            this.displayContent = ko.unwrap(this.params.displayContent);
            this.fileType = '';
            this.url = "";
            this.type = "";
            this.renderers = [];
            this.loading = ko.observable(true);
            var self = this;
            var renderer;
            init();

            function init() {
                self.scene = new THREE.Scene();
                self.scene.background = new THREE.Color( 0x000000 );
                self.camera = new THREE.PerspectiveCamera( 15, window.innerWidth / window.innerHeight, 0.01, 40 );
                self.camera.position.x = 0.4;
                self.camera.position.z = - 2;
                self.camera.up.set( 0, 0, 1 );
                self.scene.add( self.camera );
                renderer = new THREE.WebGLRenderer( { antialias: true } );
                renderer.setPixelRatio( window.devicePixelRatio );
                self.loader = new THREE.PCDLoader();
                self.controls = new THREE.TrackballControls( self.camera, renderer.domElement );
                self.controls.rotateSpeed = 2.0;
                self.controls.zoomSpeed = 0.3;
                self.controls.panSpeed = 0.2;
                self.controls.staticMoving = true;
                self.controls.minDistance = 0.3;
                self.controls.maxDistance = 0.3 * 100;
                self.renderers.push(renderer);
            }
        },
        template: { require: 'text!templates/views/components/cards/file-renderers/pcdreader.htm' }
    });
});
