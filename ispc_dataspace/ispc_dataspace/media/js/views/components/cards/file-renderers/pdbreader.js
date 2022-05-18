define(['jquery',
    'knockout',
    'three',
    'PDBLoader',
    'CSS2DRenderer',
    'TrackballControls',
    'bindings/threePDB'
], function($, ko, THREE) {
    return ko.components.register('pdbreader', {
        viewModel: function(params) {
            this.params = params;
            this.displayContent = ko.unwrap(this.params.displayContent);
            this.fileType = '';
            this.url = "";
            this.type = "";
            this.loading = ko.observable(true);
            var self = this;
            this.loader = new THREE.PDBLoader();
            self.offset = new THREE.Vector3();
            init();
            var renderer;
            var labelRenderer;

            function init() {
                self.renderers = [];
                self.scene = new THREE.Scene();
                self.params.state.scene = self.scene;
                self.scene.background = new THREE.Color( 0x000000 );
                self.camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 1, 5000 );
                self.camera.position.z = 1000;
                self.scene.add( self.camera );
                self.light = new THREE.DirectionalLight( 0xffffff, 0.8 );
                self.light.position.set( 1, 1, 1 );
                self.scene.add( self.light );
                self.light2 = new THREE.DirectionalLight( 0xffffff, 0.5 );
                self.light2.position.set( - 1, - 1, 1 );
                self.scene.add( self.light2 );
                self.root = new THREE.Group();
                self.scene.add( self.root );
                renderer = new THREE.WebGLRenderer( { antialias: true } );
                renderer.setPixelRatio( window.devicePixelRatio );
                labelRenderer = new THREE.CSS2DRenderer();
                labelRenderer.domElement.style.position = 'absolute';
                labelRenderer.domElement.style.top = '0';
                labelRenderer.domElement.style.pointerEvents = 'none';
                self.controls = new THREE.TrackballControls( self.camera, renderer.domElement );
                self.controls.minDistance = 500;
                self.controls.maxDistance = 2000;
                self.renderers.push(renderer);
                self.renderers.push(labelRenderer);
            }

        },
        template: { require: 'text!templates/views/components/cards/file-renderers/pdbreader.htm' }
    });
});
