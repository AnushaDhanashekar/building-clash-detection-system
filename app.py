#!/usr/bin/env python3
from aws_cdk import App

from pypackages.cdk.src.autodesk_cdk.identify_building_clashes.building_clashes_stack import BuildingClashesStack

app = App()
BuildingClashesStack(app, "autodesk-sandbox-building-clashes")

app.synth()