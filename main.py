from core.dpi import set_dpi_aware
set_dpi_aware()
from core.orchestrator import run

if __name__ == "__main__":
    run()

from core.sandboxie_launcher import launch_multiple

boxes = ["Box1", "Box2", "Box3", "Box4", "Box5"]
launch_multiple(boxes)
