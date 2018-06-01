import random
import string
from typing import Optional

from sqlalchemy.orm.session import Session

from tortuga.db.models.hardwareProfile import HardwareProfile
from tortuga.db.models.nic import Nic
from tortuga.db.models.node import Node
from tortuga.db.models.softwareProfile import SoftwareProfile
from tortuga.resourceAdapter.resourceAdapter import ResourceAdapter


class Dummyadapter(ResourceAdapter):
    __adaptername__ = 'dummy'

    def start(self, addNodesRequest: dict, dbSession: Session,
              dbHardwareProfile: HardwareProfile,
              dbSoftwareProfile: Optional[SoftwareProfile] = None):
        """
        Create nodes
        """

        nodes = []

        for _ in range(addNodesRequest['count']):
            random_host_name_suffix = get_random_host_name_suffix()

            node = Node(name='compute-{}'.format(random_host_name_suffix))
            node.softwareprofile = dbSoftwareProfile
            node.hardwareprofile = dbHardwareProfile
            node.isIdle = False
            node.state = 'Installed'

            # create dummy nic
            nic = Nic(boot=True, ip=generate_fake_ip())

            node.nics.append(nic)

            nodes.append(node)

        return nodes


def get_random_host_name_suffix():
    return ''.join(random.choices(string.ascii_lowercase, k=5))


def generate_fake_ip():
    return '10.10.{}.{}'.format(random.randint(1, 254), random.randint(1, 254))
