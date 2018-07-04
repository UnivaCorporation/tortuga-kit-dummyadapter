import random
import string
from typing import Optional

from sqlalchemy.orm.session import Session

from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.nic import Nic
from tortuga.db.models.node import Node
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.node import state
from tortuga.resourceAdapterConfiguration import settings
from tortuga.resourceAdapter.resourceAdapter import ResourceAdapter


class Dummyadapter(ResourceAdapter):
    __adaptername__ = 'dummy'

    settings = {
        'state': settings.StringSetting(
            description='The final state of the node after creation',
            default=state.NODE_STATE_INSTALLED,
            values=[
                state.NODE_STATE_CREATED,
                state.NODE_STATE_PROVISIONED,
                state.NODE_STATE_INSTALLED
            ]
        ),
    }

    #
    # The various states that a node will transition through, in order
    #
    STATE_TRANSITIONS = [
        state.NODE_STATE_CREATED,
        state.NODE_STATE_PROVISIONED,
        state.NODE_STATE_INSTALLED
    ]

    def start(self, addNodesRequest: dict, dbSession: Session,
              dbHardwareProfile: HardwareProfile,
              dbSoftwareProfile: Optional[SoftwareProfile] = None):
        """
        Create nodes

        """
        #
        # Load resource adapter settings
        #
        config = self.getResourceAdapterConfig(
            sectionName=addNodesRequest.get(
                'resource_adapter_configuration', 'default')
        )

        nodes = []

        for _ in range(addNodesRequest['count']):
            random_host_name_suffix = get_random_host_name_suffix()

            node = Node(name='compute-{}'.format(random_host_name_suffix))
            node.softwareprofile = dbSoftwareProfile
            node.hardwareprofile = dbHardwareProfile
            node.isIdle = False
            node.state = self.STATE_TRANSITIONS[0]

            # create dummy nic
            nic = Nic(boot=True, ip=generate_fake_ip())

            node.nics.append(nic)

            self._simulate_state_changes(
                node,
                config.get('state', self.settings['state'].default)
            )

            nodes.append(node)

        return nodes

    def _simulate_state_changes(self, node: Node, final_state: str):
        """
        Simulate the node transitioning through multiple states by firing
        state change events.

        :param Node node:       the node to transition through the state
                                changes
        :param str final_state: the final state the node must reach in the
                                simulation

        """
        initial_state_found = False

        for state in self.STATE_TRANSITIONS:
            #
            # Find the current node state in the list of transitions
            #
            if not initial_state_found:
                if state == node.state:
                    initial_state_found = True
                continue

            #
            # Fire a state change event to get to the next state
            #
            previous_state = node.state
            node.state = state
            self.fire_state_change_event(node, previous_state)

            #
            # If this is the final state, exit the loop
            #
            if state == final_state:
                break


def get_random_host_name_suffix():
    return ''.join(random.choices(string.ascii_lowercase, k=5))


def generate_fake_ip():
    return '10.10.{}.{}'.format(random.randint(1, 254), random.randint(1, 254))
