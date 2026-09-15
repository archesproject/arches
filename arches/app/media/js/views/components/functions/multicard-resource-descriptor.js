import MulticardResourceDescriptorTemplate from 'templates/views/components/functions/multicard-resource-descriptor.htm';
import ko from 'knockout';
import _ from 'underscore';
import arches from 'arches';

let parentComponent;
const setParentComponent = (found) => {
    parentComponent = found;
}
ko.components.defaultLoader.getConfig('views/components/functions/primary-descriptors', setParentComponent);

ko.components.register('views/components/functions/multicard-resource-descriptor', {
    viewModel: function(params) {
        var self = this;
        parentComponent.viewModel.apply(this, arguments);

        this.parseNodeIdsFromStringTemplate = (initialValue) => {
            const regex = /<(.*?)>/g;
            const aliases = [...initialValue.matchAll(regex)].map(matchObj => matchObj[1]);
            return self.graph.nodes.filter(n => aliases.includes(n.alias)).map(n => n.nodeid);
        }

        this.selectedNodes = {
            name: ko.observableArray(
                self.parseNodeIdsFromStringTemplate(self.name.string_template())
            ),
            description: ko.observableArray(
                self.parseNodeIdsFromStringTemplate(self.description.string_template())
            ),
            map_popup: ko.observableArray(
                self.parseNodeIdsFromStringTemplate(self.map_popup.string_template())
            ),
        };

        const sortedCards = this.graph.cards.toSorted((a, b) => {
            const nameA = a.name.toUpperCase();
            const nameB = b.name.toUpperCase();
            if (nameA < nameB) {
                return -1;
            }
            if (nameA > nameB) {
                return 1;
            }

            return 0;
        });

        this.groupedNodesForSelect2 = [];
        sortedCards.forEach(card => {
            const stringNodes = this.graph.nodes.filter(
                (node) => {
                    return (node.nodegroup_id === card.nodegroup_id);
                }
            );

            if (stringNodes.length) {
                this.groupedNodesForSelect2.push({
                    text: card.name,
                    children: stringNodes.map(node => {
                        return {
                            id: node.nodeid,
                            text: node.alias,
                        }
                    }),
                });
            }
        });

        Object.entries(this.selectedNodes).forEach(
            ([observableName, observable]) => {
                observable.subscribe(actions => {
                    actions.forEach(action => {
                        self.updateTemplate(action.value, action.status, observableName)
                    })
                }, this, 'arrayChange')
            }
        );

        this.baseSelect2Config = {
            multiple: true,
            placeholder: arches.translations.selectPrimaryDescriptionIdentifierCard,
            data: self.groupedNodesForSelect2,
        };

        this.updateTemplate = (nodeid, actionType, descriptorName) => {
            const templateObservable = params.config.descriptor_types[descriptorName].string_template;
            const priorValue = templateObservable();
            const nodeAlias = self.graph.nodes.find(n => n.nodeid === nodeid).alias;

            if (actionType === 'deleted') {
                if (priorValue.startsWith(`<${nodeAlias}>`)) {
                    templateObservable(priorValue.replace(`<${nodeAlias}>`, ''));
                } else {
                    templateObservable(priorValue.replace(` <${nodeAlias}>`, ''));
                }
            } else {
                if (priorValue === '') {
                    templateObservable(`<${nodeAlias}>`);
                } else {
                    templateObservable(`${priorValue} <${nodeAlias}>`);
                }
            }
        };
    },
    template: MulticardResourceDescriptorTemplate,
});
