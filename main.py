﻿#!/usr/bin/python3.3

import engine.EngineCore as EngineCore
import engine.Reloadable as Reloadable
import engine.testmodules.font_testing as font_testing
import game.start as game
import engine.HTransformable

#EngineCore.testLoading()
#EngineCore.testFIFOScheduling()
#EngineCore.testWindowModule()
#Reloadable.testReloadable()
#font_testing.text_test1()
#engine.HTransformable.testTransformable()
game.bootstrap_game()
exit()