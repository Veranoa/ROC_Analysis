#!/bin/bash

# PyInstaller 
pyinstaller pyinstaller.spec

# create dmg 
hdiutil create -volname ROCAnalyser -srcfolder dist/ROCAnalyser.app -ov -format UDZO ROCAnalyser.dmg
