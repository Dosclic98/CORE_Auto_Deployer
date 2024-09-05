from core.emulator.coreemu import CoreEmu
from core.emulator.data import IpPrefixes
from core.emulator.enumerations import EventTypes
from core.nodes.base import CoreNode, Position
from core.nodes.network import SwitchNode
import shutil
import traceback 

EXECPATH = "/mnt/c/Users/savarro/OneDrive - RSE S.P.A/Desktop/Materiale_Uni/Progetti/CORE_Scenarios/CORE_Auto_Deployer/executables"
CLIFOLDER = "client_MMS"
SERFOLDER = "server_MMS"
TMPFOLDERPREFIX = "pycore"

def copyToNode(node: CoreNode, isClient: bool, sessionId: int):
    fromPath = f"{EXECPATH}/{CLIFOLDER}" if isClient else f"{EXECPATH}/{SERFOLDER}"
    toPath = f"/tmp/pycore.{sessionId}/{node.name}.conf/{CLIFOLDER}" if isClient else f"/tmp/pycore.{sessionId}/{node.name}.conf/{SERFOLDER}" 

    shutil.copytree(fromPath, toPath)

#def startClient(node: CoreNode, sessionId: int):


def main():
    try:
        # Setup ip prefixes
        ipPrefixes = IpPrefixes(ip4_prefix="10.0.0.0/24")

        # Initialize CoreEmu object and session (setting session
        # state as CONFIGURATION_STATE to allow the configuration phase)
        coreEmu = globals().get("coreemu", CoreEmu())
        session = coreEmu.create_session()
        print(f"Session id: {session.id}")
        session.set_state(EventTypes.CONFIGURATION_STATE)
        
        # Create nodes
        switch = session.add_node(SwitchNode, name = "switch", position=Position(x=200, y=200))
        n1 = session.add_node(CoreNode, name = "n1", position=Position(x=100, y=100))
        n2 = session.add_node(CoreNode, name = "n2", position=Position(x=300, y=100))

        # Link node to switches
        iface = ipPrefixes.create_iface(n1)
        session.add_link(n1.id, switch.id, iface)
        iface = ipPrefixes.create_iface(n2)
        session.add_link(n2.id, switch.id, iface)

        # Start session
        session.instantiate()

        # Copy client and server files to the CORE nodes 
        copyToNode(node=n1, isClient=True, sessionId=session.id)
        copyToNode(node=n2, isClient=False, sessionId=session.id)

        input("Press enter to end the session...")

        # Shutdown session
        coreEmu.shutdown()
        
    except:
        # printing stack trace 
        traceback.print_exc()
        coreEmu.shutdown()



if __name__ == "__main__":
    main()