from __future__ import annotations

import firefly.domain as ffd

from ..messaging.system_bus import SystemBusAware


class Kernel(SystemBusAware):
    def boot(self):
        self.invoke(ffd.LoadContainers())
