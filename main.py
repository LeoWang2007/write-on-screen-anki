import aqt.addons

from . import utils
from .utils import __addon_name__, __version__
from .utils import _language

from aqt import mw, dialogs
from aqt.utils import showWarning

from anki import lang
from anki.hooks import addHook

from PyQt6.QtWidgets import QMenu, QColorDialog, QMessageBox, QInputDialog
from PyQt6 import QtCore
from PyQt6.QtGui import QKeySequence, QAction
from PyQt6.QtGui import QColor
from PyQt6.QtCore import pyqtSlot as slot

import os

# This declarations are there only to be sure that in case of troubles
# with "profileLoaded" hook everything will work.

ts_state_on = False
ts_profile_loaded = False

ts_color = "#272828"
ts_line_width = 4
ts_opacity = 0.7
ts_default_review_html = mw.reviewer.revHtml


@slot()
def ts_change_color():
    """
    Open color picker and set chosen color to text (in content)
    """
    global ts_color
    qcolor_old = QColor(ts_color)
    qcolor = QColorDialog.getColor(qcolor_old)
    if qcolor.isValid():
        ts_color = qcolor.name()
        execute_js("color = '" + ts_color + "'; update_pen_settings()")
        ts_refresh()


@slot()
def ts_change_width():
    global ts_line_width
    value, accepted = QInputDialog.getDouble(mw, "Touch Screen", "Enter the width:", ts_line_width)
    if accepted:
        ts_line_width = value
        execute_js("line_width = '" + str(ts_line_width) + "'; update_pen_settings()")
        ts_refresh()


@slot()
def ts_change_opacity():
    global ts_opacity
    value, accepted = QInputDialog.getDouble(mw, "Touch Screen", "Enter the opacity (100 = transparent, 0 = opaque):",
                                             100 * ts_opacity, 0, 100, 2)
    if accepted:
        ts_opacity = value / 100
        execute_js("canvas.style.opacity = " + str(ts_opacity))
        ts_refresh()


@slot()
def ts_about():
    """
    Show "about" window.
    """
    ts_about_box = QMessageBox(mw)
    ts_about_box.parent = mw
    ts_about_box.setText(
        f"{__addon_name__}{__version__}\n感谢你的使用\nHave a nice day. \n基于https://ankiweb.net/shared/info/1631622775创作\nBased on https://ankiweb.net/shared/info/1631622775")
    ts_about_box.setFixedSize(250, 150)
    ts_about_box.setWindowTitle("About " + __addon_name__ + " " + __version__)

    ts_about_box.exec()


def ts_save():
    """
    Saves configurable variables into profile, so they can
    be used to restore previous state after Anki restart.
    """
    mw.pm.profile['ts_state_on'] = ts_state_on
    mw.pm.profile['ts_color'] = ts_color
    mw.pm.profile['ts_line_width'] = ts_line_width
    mw.pm.profile['ts_opacity'] = ts_opacity


def ts_load():
    """
    Load configuration from profile, set states of checkable menu objects
    and turn on night mode if it were enabled on previous session.
    """
    global ts_state_on, ts_color, ts_profile_loaded, ts_line_width, ts_opacity

    try:
        ts_state_on = mw.pm.profile['ts_state_on']
        ts_color = mw.pm.profile['ts_color']
        ts_line_width = mw.pm.profile['ts_line_width']
        ts_opacity = mw.pm.profile['ts_opacity']
    except KeyError:
        ts_state_on = False
        ts_color = "#0070d9"
        ts_line_width = 4
        ts_opacity = 0.8
    ts_profile_loaded = True

    if ts_state_on:
        ts_on()

    assure_plugged_in()


def execute_js(code):
    web_object = mw.reviewer.web
    web_object.eval(code)


def assure_plugged_in():
    global ts_default_review_html

    if not mw.reviewer.revHtml == custom:
        ts_default_review_html = mw.reviewer.revHtml
        mw.reviewer.revHtml = custom


def clear_blackboard(web_object=None):
    assure_plugged_in()

    if not web_object:
        web_object = mw.reviewer.web

    if ts_state_on:
        javascript = 'clear_canvas();'
        web_object.eval(javascript)


def ts_resize(html, card, context):
    if ts_state_on:
        html += """
        <script>
        var ts_interval;
        if(ts_interval === undefined){
            if(resize !== undefined)
                ts_interval = window.setInterval(resize, 750);
        }
        </script>
        """
    return html


def ts_onload():
    """
    Add hooks and initialize menu.
    Call to this function is placed on the end of this file.
    """

    addHook("unloadProfile", ts_save)
    addHook("profileLoaded", ts_load)
    addHook("showQuestion", clear_blackboard)
    addHook('prepareQA', ts_resize)
    ts_setup_menu()


ts_blackboard = utils.tools.readFile(os.path.join(utils.paths.ADDON_ROOT, "pages", "blackboard.html"))


def custom(*args, **kwargs):
    global ts_state_on
    default = ts_default_review_html(*args, **kwargs)
    if not ts_state_on:
        return default
    output = (
            default +
            ts_blackboard +
            f"""
        <script>
        color = '{ts_color}'
        line_width = '{ts_line_width}'
        document.querySelector("#main_canvas").style.opacity = '{ts_opacity}'
        </script>
        """

    )
    return output


mw.reviewer.revHtml = custom


def ts_on():
    """
    Turn on
    """
    if not ts_profile_loaded:
        showWarning(_language.TS_ERROR_NO_PROFILE)
        return False

    global ts_state_on
    ts_state_on = True
    ts_menu_switch.setChecked(True)
    return True


def ts_off():
    """
    Turn off
    """
    if not ts_profile_loaded:
        showWarning(_language.TS_ERROR_NO_PROFILE)
        return False

    global ts_state_on
    ts_state_on = False
    ts_menu_switch.setChecked(False)
    return True


@slot()
def ts_switch():
    """
    Switch TouchScreen.
    """

    if ts_state_on:
        ts_off()
    else:
        ts_on()

    # Reload current screen.

    if mw.state == "review":
        mw.moveToState('overview')
        mw.moveToState('review')
    if mw.state == "deckBrowser":
        mw.deckBrowser.refresh()
    if mw.state == "overview":
        mw.overview.refresh()


def ts_refresh():
    """
    Refresh display by reenabling night or normal mode.
    """
    if ts_state_on:
        ts_on()
    else:
        ts_off()


def ts_setup_menu():
    """
    Initialize menu. If there is an entity "View" in top level menu
    (shared with other plugins, like "Zoom" of R. Sieker) options of
    the addon will be placed there. In other case it creates that menu.
    """
    global ts_menu_switch

    mw.addon_view_menu = mw.form.menuqt_accel_view

    mw.form.menubar.insertMenu(mw.form.menuTools.menuAction(), mw.addon_view_menu)

    mw.ts_menu = QMenu(_language.ADDON_NAME, mw)

    mw.addon_view_menu.addMenu(mw.ts_menu)

    ts_menu_switch = QAction(_language.ENABLE_ADDON, mw, checkable=True)
    ts_menu_color = QAction(_language.MENU_PEN_COLOR, mw)
    ts_menu_width = QAction(_language.MENU_PEN_WIDTH, mw)
    ts_menu_opacity = QAction(_language.MENU_PEN_OPACITY, mw)
    ts_menu_about = QAction(_language.MENU_ABOUT, mw)

    ts_toggle_seq = QKeySequence("Ctrl+r")
    ts_menu_switch.setShortcut(ts_toggle_seq)

    mw.ts_menu.addAction(ts_menu_switch)
    mw.ts_menu.addAction(ts_menu_color)
    mw.ts_menu.addAction(ts_menu_width)
    mw.ts_menu.addAction(ts_menu_opacity)
    mw.ts_menu.addSeparator()
    mw.ts_menu.addAction(ts_menu_about)

    ts_menu_switch.triggered.connect(ts_switch)
    ts_menu_color.triggered.connect(ts_change_color)
    ts_menu_width.triggered.connect(ts_change_width)
    ts_menu_opacity.triggered.connect(ts_change_opacity)
    ts_menu_about.triggered.connect(ts_about)
