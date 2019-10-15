from __future__ import annotations

import firefly.domain as ffd

from .framework_event import FrameworkEvent
from ..entity.entity import required


class DeploymentCreated(FrameworkEvent):
    deployment: ffd.Deployment = required()
