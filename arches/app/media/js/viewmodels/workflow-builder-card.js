define([
  'jquery',
  'underscore',
  'knockout',
  'knockout-mapping',
  'arches',
  'templates/views/viewmodels/workflow-builder-card.htm',
  'views/components/workflows/workflow-component-abstract',
  'viewmodels/alert',
  'views/components/plugins/workflow-builder-loader'
], function ($, _, ko, koMapping, arches, template, WorkflowComponentAbstract, AlertViewModel) {
  const WorkflowBuilderCard = function (params) {
    _.extend(this, params);

    this.cardHasLoaded = ko.observable(false);

    this.workflowComponentAbstract = ko.observable();
    this.isStepActive = ko.observable(false);
    this.currentComponentData = ko.observable();

    this.selectedNodegroup = ko.observable(0);

    this.parentTile = ko.observable();

    // Annoyingly 'one' as the ID will be selected when
    // 'none' is selected because the code does an includes check
    this.tileManagedOptions = ko.observableArray([
      { text: 'One', id: 'tile_one' },
      { text: 'Many', id: 'tile_many' },
      { text: 'None', id: 'tile_none' }
    ]);
    this.selectedTileManaged = ko.observable('tile_one');

    this.selectedHiddenNodes = ko.observableArray();
    this.pushBackTimeout = ko.observable();

    this.selectedResourceIdPath = ko.observable(0);

    this.configKeys = ko.observable({ placeholder: 0 });

    this.cardIdx = this.parentStep.cardIdx(this.cardId);

    this.loadAbstractComponent = (componentData) => {
      this.isStepActive(false);
      let workflowCA = new WorkflowComponentAbstract({
        componentData: componentData,
        workflowComponentAbstractId: null,
        isValidComponentPath: () => undefined,
        getDataFromComponentPath: () => undefined,
        lockExternalStep: () => undefined,
        title: 'Step title',
        isStepSaving: false,
        locked: false,
        workflowHistory: {
          componentdata: null
        },
        lockableExternalSteps: [],
        workflowId: '',
        alert: null,
        outerSaveOnQuit: null,
        isStepActive: this.isStepActive
      });
      /**
       * This endpoint was created only to add additional tiles
       * that don't exist. These tiles are used to provide additional
       * cards to the topCards.
       *
       * For example the 'Location Data' nodegroup has nested nodegroups.
       * These nodegroups will only load if the parent tile (Location Data)
       * exists in the returned tiles because the tile will provide the cards.
       *
       * A dummy-id has been created to match the tile returned to the parenttileid
       * of the node config. This will eventually need to be changed if there
       * are multiple components that require a parenttileid.
       */
      workflowCA.getCardResourceIdOrGraphId = () => {
        return this.graphId() + '/override';
      };
      this.isStepActive(true);
      this.workflowComponentAbstract(workflowCA);
    };

    this.graphId = ko.computed(() => {
      if (this.currentComponentData()?.parameters.graphid) {
        return this.currentComponentData().parameters.graphid;
      }
      const searchParams = new URLSearchParams(window.location.search);
      const graphId = searchParams.get('graph-id');
      if (graphId) {
        return graphId;
      }
      return params.graphId;
    }, this);

    this.nodegroupOptions = ko.computed(() => {
      return (
        this.parentStep?.parentWorkflow?.graphNodegroupOptions()?.[this.graphId()] || [
          {
            text: 'None',
            nodegroupId: '',
            id: 0
          }
        ]
      );
    }, this);

    this.graphCards = ko.computed(() => {
      return (
        this.parentStep?.parentWorkflow?.graphCards()?.[this.graphId()] || {
          nodes: [],
          cardwidgets: [],
          cards: [],
          nodegroups: [],
          tiles: []
        }
      );
    }, this);

    this.loadComponent = () => {
      if (!this.currentComponentData()) return;
      this.selectedNodegroup(
        this.nodegroupOptions().findIndex(
          (option) => option.nodegroupId === this.currentComponentData().parameters.nodegroupid
        )
      );
      this.selectedTileManaged('tile_' + this.currentComponentData().tilesManaged);
      this.selectedHiddenNodes(this.currentComponentData().parameters.hiddenNodes);
      const resourceIdPathIdx = this.workflowResourceIdPathOptions().findIndex(
        (option) => option.resourceIdPath === this.currentComponentData().parameters.resourceid
      );
      this.selectedResourceIdPath(resourceIdPathIdx !== -1 ? resourceIdPathIdx : 0);
      this.configureParentTile(this.currentComponentData().parameters.nodegroupid);
      if (this.currentComponentData().parameters.nodegroupid) {
        this.loadAbstractComponent(this.currentComponentData());
      }
    };

    this.title = ko.computed(() => {
      return (
        `${this.cardIdx()}: ${this.nodegroupOptions()[this.selectedNodegroup()]?.text}` ||
        'New Card'
      );
    }, this);

    this.hiddenNodeOptions = ko.computed(() => {
      if (!this.currentComponentData()) return [];
      const cardWidgets = this.graphCards().cardwidgets.map((widget) => {
        return {
          node_id: widget.node_id,
          visible: widget.visible
        };
      });
      const nodes = this.graphCards().nodes.filter((node) => {
        const hasWidget = cardWidgets.find((widget) => {
          return widget.visible && widget.node_id === node.nodeid;
        });
        return (
          hasWidget &&
          node.nodegroup_id === this.currentComponentData().parameters.nodegroupid &&
          node.datatype !== 'semantic' &&
          node.nodeid !== node.nodegroup_id
        );
      });
      return nodes.map((node) => {
        return {
          text: node.name,
          id: node.nodeid
        };
      });
    }, this);

    this.configureParentTile = (nodegroupId) => {
      /**
       * Nodegroups that require a parent tile are discovered
       * on the backend and identified here.
       */
      const cardNodegroup = this.graphCards().nodegroups.find((nodegroup) => {
        return nodegroup.nodegroupid == nodegroupId;
      });
      const parentTile = this.graphCards().tiles.find((tile) => {
        return tile.nodegroup_id === cardNodegroup?.parentnodegroup_id;
      });
      this.parentTile(null);
      if (parentTile) {
        const parentSemanticName = this.nodegroupOptions().find(
          (nodegroup) => nodegroup.nodegroupId === parentTile.nodegroup_id
        ).text;
        const camelCaseName = (() => {
          const parts = parentSemanticName.split(' ');
          parts[0] = parts[0].toLowerCase();
          return parts.join('');
        })();
        this.parentTile({
          parentNodegroupId: parentTile.nodegroup_id,
          lookupName: camelCaseName
        });
      }
      this.currentComponentData().parameters.parenttileid = parentTile?.tileid;
    };

    this.setupSubscriptions = () => {
      this.selectedTileManaged.subscribe((value) => {
        this.currentComponentData().tilesManaged = value?.replace('tile_', '');
        this.loadAbstractComponent(this.currentComponentData());
      });

      this.selectedNodegroup.subscribe((value) => {
        const data = JSON.parse(JSON.stringify(this.nodegroupOptions()[value].component));
        data.parameters.resourceid = '';

        /**
         * Using a UUID here but it would be better to have
         * a readable name.
         */
        data.uniqueInstanceName = this.cardId;
        this.currentComponentData(data);
        this.configureParentTile(data.parameters.nodegroupid);
        this.loadAbstractComponent(this.currentComponentData());
      });

      this.selectedHiddenNodes.subscribe((value) => {
        this.currentComponentData().parameters.hiddenNodes = value;
        this.cardHasLoaded(false);
        if (this.pushBackTimeout) {
          clearTimeout(this.pushBackTimeout());
        }
        this.pushBackTimeout(setTimeout(() => {
          this.loadAbstractComponent(this.currentComponentData());
          this.cardHasLoaded(true);
        }, 2000));
      });
    };

    this.removeCard = () => {
      this.parentStep.removeCardFromStep(this.cardId);
    };

    this.shiftCard = (direction) => {
      this.parentStep.shiftCard(this.cardId, direction);
    };

    this.workflowResourceIdPathOptions = ko.computed(() => {
      return this.parentStep.parentWorkflow.workflowResourceIdPathOptions();
    });

    /**
     * FIXME: Could be prone to bugs
     */
    this.isInitialStep = ko.computed(() => {
      const index = this.workflowResourceIdPathOptions().findIndex((path) => {
        return (
          path.resourceIdPath?.includes(this.cardId) &&
          path.resourceIdPath?.includes(this.parentStep.stepName())
        );
      });
      return index == 1;
    }, this);

    this.componentName = ko.computed(() => {
      const WORKFLOW_BUILDER_INITIAL_STEP_COMPONENT = 'workflow-builder-initial-step';
      const DEFAULT_CARD_UTIL_COMPONENT = 'default-card';
      const currentComponentName = this.currentComponentData()?.componentName;
      if (
        currentComponentName &&
        currentComponentName !== WORKFLOW_BUILDER_INITIAL_STEP_COMPONENT &&
        currentComponentName !== DEFAULT_CARD_UTIL_COMPONENT
      ) {
        return currentComponentName;
      }
      return this.isInitialStep()
        ? WORKFLOW_BUILDER_INITIAL_STEP_COMPONENT
        : DEFAULT_CARD_UTIL_COMPONENT;
    });

    this.getComponentData = () => {
      const { tilesManaged, uniqueInstanceName, parameters } = this.currentComponentData() || {};
      const { graphid, nodegroupid, semanticName, hiddenNodes } = parameters || {};
      const { resourceIdPath } =
        this.workflowResourceIdPathOptions()[this.selectedResourceIdPath()];

      const componentData = {
        componentName: this.componentName(),
        tilesManaged: tilesManaged,
        uniqueInstanceName: uniqueInstanceName,
        parameters: {
          ...(params?.componentData?.parameters || {}), // Custom params can be provided manually
          graphid: graphid,
          nodegroupid: nodegroupid,
          resourceid: resourceIdPath,
          semanticName: semanticName,
          hiddenNodes: hiddenNodes
        }
      };

      if (this.parentTile()) {
        /**
         * FIXME: Again relying on the initial step always being the first
         * - Same as isInitialStep
         */
        const { basePath } = this.workflowResourceIdPathOptions()?.[1];
        const parentTileIdPath = basePath + `['${this.parentTile().lookupName}']`;
        componentData.parameters.parenttileid = parentTileIdPath;
      }

      if (this.isInitialStep()) {
        const parentTiles = this.parentStep.parentWorkflow.getRequiredParentTiles();
        if (parentTiles.length) {
          componentData.parameters.requiredParentTiles =
            this.parentStep.parentWorkflow.getRequiredParentTiles();
        }
      }

      return componentData;
    };

    this.init = async () => {
      if (this.componentData) {
        this.currentComponentData(JSON.parse(JSON.stringify(this.componentData)));
      }
      this.loadComponent();
      this.setupSubscriptions();
      this.cardHasLoaded(true);
    };

    this.init();
  };

  ko.components.register('workflow-builder-card', {
    template: template
  });

  return WorkflowBuilderCard;
});
