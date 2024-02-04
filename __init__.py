# -*- coding: utf-8 -*-
# 版权所有 Copyright: WatermelonCloud Github@LeoWang2007

"""
About Source Code

基于https://ankiweb.net/shared/info/1631622775创作
Based on https://ankiweb.net/shared/info/1631622775

原作者似乎已停止维护，因为我刚好也有此需求就接手了项目
The original author seems to have not fixed it for a long time, so I restarted the project.

License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

此插件可以像苹果版Anki一样实现手写板效果
This plugin adds the function of touchscreen, similar that one implemented in Anki for iOS.

你可以在“View菜单中进行一些操作”
It adds a "view" menu entity with options like:

    switching touchscreen
    modifying some of the colors

Important parts of Javascript code inspired by http://creativejs.com/tutorials/painting-with-pixels/index.html
"""

# =====
# Traveler, as you set off on your journey once again, you must remember that the journey itself has meaning.
# Wonderful things is coming...
from . import main
main.ts_onload()
