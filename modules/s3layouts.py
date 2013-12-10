# -*- coding: utf-8 -*-

""" Sahana Eden GUI Layouts (HTML Renderers)

    @copyright: 2012-13 (c) Sahana Software Foundation
    @license: MIT

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.

    @todo: - complete layout implementations
           - render "selected" (flag in item)
"""

__all__ = ["S3MainMenuDefaultLayout",
           "S3OptionsMenuDefaultLayout",
           "S3MenuSeparatorDefaultLayout",
           "S3MainMenuLayout", "MM",
           "S3OptionsMenuLayout", "M",
           "S3MenuSeparatorLayout", "SEP",
           "S3BreadcrumbsLayout",
           "S3AddResourceLink",
           "homepage",
           ]

from gluon import *
from gluon.storage import Storage
from s3 import *

# =============================================================================
class S3MainMenuDefaultLayout(S3NavigationItem):
    """ Application Main Menu Layout """

    @staticmethod
    def layout(item):

        # Manage flags: hide any disabled/unauthorized items
        if not item.authorized:
            item.enabled = False
            item.visible = False
        elif item.enabled is None or item.enabled:
            item.enabled = True
            item.visible = True

        if item.enabled and item.visible:

            items = item.render_components()
            if item.parent is not None:
                if item.opts.right:
                    _class = "fright"
                else:
                    _class = "fleft"
                if item.components:
                    # Submenu, render only if there's at list one active item
                    if item.get_first(enabled=True):
                        _href = item.url()
                        return LI(DIV(A(item.label,
                                        _href=_href,
                                        _id=item.attr._id),
                                        _class="hoverable"),
                                  UL(items,
                                     _class="submenu"),
                                  _class=_class)
                else:
                    # Menu item
                    if item.parent.parent is None:
                        # Top-level item
                        _href = item.url()
                        if item.is_first():
                            # 1st item, so display logo
                            link = DIV(SPAN(A("",
                                              _href=_href),
                                              _class="S3menulogo"),
                                       SPAN(A(item.label, _href=_href),
                                              _class="S3menuHome"),
                                       _class="hoverable")
                        else:
                            link = DIV(A(item.label,
                                         _href=item.url(),
                                         _id=item.attr._id),
                                       _class="hoverable")
                        return LI(link, _class=_class)
                    else:
                        # Submenu item
                        if isinstance(item.label, dict):
                            if "id" in item.label:
                                return S3MainMenuLayout.checkbox_item(item)
                            elif "name" in item.label:
                                label = item.label["name"]
                            else:
                                return None
                        else:
                            label = item.label
                        if item.ltr:
                            _class = "ltr"
                        else:
                            _class = ""
                        link = A(label, _href=item.url(), _id=item.attr._id,
                                 _class=_class)
                        return LI(link)
            else:
                # Main menu
                return UL(items, _id="modulenav")

        else:
            return None

    # ---------------------------------------------------------------------
    @staticmethod
    def checkbox_item(item):
        """ Render special active items """

        name = item.label
        link = item.url()
        _id = name["id"]
        if "name" in name:
            _name = name["name"]
        else:
            _name = ""
        if "value" in name:
            _value = name["value"]
        else:
            _value = False
        if "request_type" in name:
            _request_type = name["request_type"]
        else:
            _request_type = "ajax"
        if link:
            if _request_type == "ajax":
                _onchange="var val=$('#%s:checked').length;" \
                          "$.getS3('%s'+'?val='+val, null, false, null, false, false);" % \
                          (_id, link)
            else:
                # Just load the page. Use this if the changed menu
                # item should alter the contents of the page, and
                # it's simpler just to load it.
                _onchange="location.href='%s'" % link
        else:
            _onchange=None
        return LI(A(INPUT(_type="checkbox",
                            _id=_id,
                            value=_value,
                            _onchange=_onchange),
                    " %s" % _name,
                    _nowrap="nowrap"))

# =============================================================================
class S3OptionsMenuDefaultLayout(S3NavigationItem):
    """ Controller Options Menu Layout """

    @staticmethod
    def layout(item):

        # Manage flags: hide any disabled/unauthorized items
        if not item.authorized:
            enabled = False
            visible = False
        elif item.enabled is None or item.enabled:
            enabled = True
            visible = True

        if enabled and visible:

            items = item.render_components()
            if item.parent is not None:
                if item.components:
                    # Submenu
                    _href = item.url()
                    return LI(DIV(A(item.label,
                                    _href=_href,
                                    _id=item.attr._id),
                                  _class="hoverable"),
                              UL(items,
                                 _class="submenu"))
                else:
                    # Menu item
                    if item.parent.parent is None:
                        # Top level item
                        return LI(DIV(A(item.label,
                                        _href=item.url(),
                                        _id=item.attr._id),
                                      _class="hoverable"))
                    else:
                        # Submenu item
                        return LI(A(item.label,
                                    _href=item.url(),
                                    _id=item.attr._id))
            else:
                # Main menu
                return UL(items, _id="subnav")

        else:
            return None

# =============================================================================
class S3MenuSeparatorDefaultLayout(S3NavigationItem):
    """ Simple menu separator """

    @staticmethod
    def layout(item):

        if item.parent is not None:
            return LI(HR(), _class="menu_separator")
        else:
            return None

# =============================================================================
# Import menu layouts from template (if present)
#
S3MainMenuLayout = S3MainMenuDefaultLayout
S3OptionsMenuLayout = S3OptionsMenuDefaultLayout
S3MenuSeparatorLayout = S3MenuSeparatorDefaultLayout

application = current.request.application
theme = current.deployment_settings.get_theme()

layouts = "applications.%s.private.templates.%s.layouts" % (application, theme)
try:
    exec("import %s as deployment_layouts" % layouts)
except:
    pass
else:
    if "S3MainMenuLayout" in deployment_layouts.__dict__:
        S3MainMenuLayout = deployment_layouts.S3MainMenuLayout
    if "S3OptionsMenuLayout" in deployment_layouts.__dict__:
        S3OptionsMenuLayout = deployment_layouts.S3OptionsMenuLayout
    if "S3MenuSeparatorLayout" in deployment_layouts.__dict__:
        S3MenuSeparatorLayout = deployment_layouts.S3MenuSeparatorLayout

# =============================================================================
# Shortcuts for menu construction
#
M = S3OptionsMenuLayout
MM = S3MainMenuLayout
SEP = S3MenuSeparatorLayout

# =============================================================================
class S3BreadcrumbsLayout(S3NavigationItem):
    """ Breadcrumbs layout """

    @staticmethod
    def layout(item):

        if item.parent is None:
            items = item.render_components()
            return DIV(UL(items), _class='breadcrumbs')
        else:
            if item.is_last():
                _class = "highlight"
            else:
                _class = "ancestor"
            return LI(A(item.label, _href=item.url(), _class=_class))

# =============================================================================
class S3AddResourceLink(S3NavigationItem):
    """
        Links in form fields comments to show a form for adding
        a new foreign key record.
    """

    def __init__(self,
                 label=None,
                 c=None,
                 f=None,
                 t=None,
                 vars=None,
                 info=None,
                 title=None,
                 tooltip=None,
                 ):
        """
            Constructor

            @param c: the target controller
            @param f: the target function
            @param t: the target table (defaults to c_f)
            @param vars: the request vars (format="popup" will be added automatically)
            @param label: the link label (falls back to label_create_button)
            @param info: hover-title for the label
            @param title: the tooltip title
            @param tooltip: the tooltip text
        """

        if label is None:
            label = title
        if info is None:
            info = title

        if c is None:
            # Fall back to current controller
            c = current.request.controller

        if label is None:
            # Fall back to label_create_button
            if t is None:
                t = "%s_%s" % (c, f)
            label = S3CRUD.crud_string(t, "label_create_button")

        return super(S3AddResourceLink, self).__init__(label,
                                                       c=c, f=f, t=t,
                                                       m="create",
                                                       vars=vars,
                                                       info=info,
                                                       title=title,
                                                       tooltip=tooltip,
                                                       mandatory=True)

    # -------------------------------------------------------------------------
    @staticmethod
    def layout(item):
        """ Layout for popup link """

        if not item.authorized:
            return None

        popup_link = A(item.label,
                       _href=item.url(format="popup"),
                       _class="s3_add_resource_link",
                       _id="%s_add" % item.function,
                       _target="top",
                       _title=item.opts.info,
                       )

        tooltip = item.opts.tooltip
        if tooltip is not None:
            ttip = DIV(_class="tooltip",
                       _title="%s|%s" % (item.opts.title, tooltip))
        else:
            ttip = ""

        return DIV(popup_link, ttip)

    # -------------------------------------------------------------------------
    @staticmethod
    def inline(item):
        """ Render this link for an inline component """

        if not item.authorized:
            return None
        
        popup_link = A(item.label,
                       _href=item.url(format="popup"),
                       _class="s3_add_resource_link action-lnk",
                       _id="%s_%s_add" % (item.vars["caller"], item.function),
                       _target="top",
                       _title=item.opts.info,
                       )

        return DIV(popup_link, _class="s3_inline_add_resource_link")

# =============================================================================
def homepage(module=None, *match, **attr):
    """
        Shortcut for module homepage menu items using the MM layout,
        retrieves the module's nice name.

        @param module: the module's prefix (controller)
        @param match: additional prefixes
        @param attr: attributes for the navigation item
    """

    settings = current.deployment_settings
    all_modules = settings.modules

    layout = S3MainMenuLayout
    c = [module] + list(match)

    if "name" in attr:
        name = attr["name"]
        attr.pop("name")
    else:
        if module is None:
            module = "default"
        if module in all_modules:
            m = all_modules[module]
            name = m.name_nice
        else:
            name = module

    if "f" in attr:
        f = attr["f"]
        del attr["f"]
    else:
        f = "index"

    return layout(name, c=c, f=f, **attr)

# =============================================================================
class S3Button(S3NavigationItem):
    """
        Generic button
    """

    # Method names
    # @ToDo: Everyone has their own list of methods. Can't we share?
    # @ToDo: Fill in the tables below for these methods.
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    SEARCH = "search"
    REPORT = "report"
    DISPLAY = "display"
    MAP = "map"
    SUMMARY = "summary"
    LOGIN = "login"
    # Not all requests have explicit methods nor methods that can be inferred,
    # e.g. some are for custom functions. Provide generic defaults for those.
    NOMETHOD = "NOMETHOD"

    # Action <--> Method, for any actions whose name is not also the method.
    # @ToDo: Find out if "list", "summary", and "copy" can be added to
    # S3Permission.METHODS.  If so, they do not have to be replaced here by the
    # method with equivalent permission, i.e. "list", "summary" -> "read", and
    # "copy" -> "create".
    ACTION_METHOD = {"edit": UPDATE,
                     "add": CREATE,
                    }

    # Tooltips for buttons default to the appropriate crud string associated
    # with the method but the key for each method differs.
    # @ToDo: We don't have crud strings for all methods, e.g. read, summary.
    CRUD_NAMES = {CREATE: "label_create_button",
                  READ: "title_display",
                  UPDATE: "title_update",
                  DELETE: "label_delete_button",
                  LIST: "label_list_button",
                  SEARCH: "title_search",
                  REPORT: "title_report",
                  DISPLAY: "title_display",
                  MAP: "title_map",
                 }

    # Standard button class.
    STANDARD_BUTTON = "action-btn"
    # Classes for bootstrap buttons.
    BOOTSTRAP_PRIMARY = "btn btn-primary"
    BOOTSTRAP_DANGER = "btn btn-danger"
    BOOTSTRAP_DEFAULT = "btn"  # Add btn-default if we want to control the style.

    # Icon classes for datalist buttons. Fallback if no icon is a labeled button.
    # @ToDo: Will we always want big-add, or should we pass it in?
    DL_BUTTON_ICON = {NOMETHOD: "icon-asterisk",
                      CREATE: "icon-plus-sign big-add",
                      UPDATE: "icon-edit",
                      DELETE: "icon-trash",
                      LOGIN: "icon-signin",
                     }

    # Method and extension for datalist button href. Delete does not have an href.
    DL_BUTTON_ARG = {NOMETHOD: "",
                     CREATE: "create.popup",
                     UPDATE: "update.popup",
                     DELETE: "",
                     LOGIN: "",
                    }

    # Datalist button class.
    DL_BUTTON_CLASS = {NOMETHOD: "",
                       CREATE: "s3_modal",
                       UPDATE: "s3_modal",
                       DELETE: "dl-item-delete",
                       LOGIN: "",
                      }

    # Additional bootstrap classes. Container buttons get primary styling.
    # @ToDo: Only add "btn" and let user pass in btn-primary.
    DL_BUTTON_BOOTSTRAP = {UPDATE: BOOTSTRAP_DEFAULT,
                           CREATE: BOOTSTRAP_PRIMARY,
                           UPDATE: BOOTSTRAP_DEFAULT,
                           DELETE: BOOTSTRAP_DANGER,
                           LOGIN: BOOTSTRAP_DEFAULT,
                          }

    def __init__(self,
                 label=None,
                 a=None,
                 c=None,
                 f=None,
                 m=None,
                 p=None,
                 t=None,
                 args=None,
                 vars=None,
                 extension=None,
                 r=None,
                 url=None,
                 title=None,
                 tooltip=None,
                 icon=None,
                 _id=None,
                 _name=None,
                 _class=None,
                 _title=None,
                 _type=None,
                 _value=None,
                 **attributes
                ):
        """
            Constructor

            Currently supports CRUD and action buttons in either the standard
            format, for full-sized web pages, or in datalist button format, for
            use on datalist items, which may be in "card" elements, or on
            datalist container widgets.

            The only required parameters for CRUD buttons are the controller and
            function or the table name (which may be supplied as the request r).
            If the button acts on a specific record, then id is needed
            (except for a datalist button delete). For purposes of setting the
            icon and style, the method defaults to "list" if no id is specified,
            else "update". 
            
            For datalist buttons, the listid is required. This is the HTML id
            property of the datalist that contains this item, or "datalist".

            @param a: the application (defaults to current.request.application)
            @param c: the controller / module
            @param f: the function / resource
            @param t: the table name
            @param m: the method or action -- this can be supplied as the
                   method, e.g. "list", "summary", "update", "delete",... or
                   the button action, e.g. "edit" or "add"
            @param args: the URL arguments list
            @param vars: the URL variables dict
            @param extension: the URL extension
            @param id: the id of the record to act on (if any) in the given
                   table t or the table specified by c and f

            @param r: the request to default the above from
            
            @param url: custom href URL, overrides URL constructed from the above

            @param label: custom button label
            @param title: custom tooltip title
            @param tooltip: custom tooltip text
            @param icon: custom icon class name (does not include "icon")
            @param crud_name: the name of the crud_strings element to use if
                   label or tooltip is not specified and the default crud
                   string (based on method) is not wanted.

            # Normally, the following are not specified.
            # @ToDo: Allow these to completely override the layout params?
            @param _id: the HTML id
            @param _name: the HTML name
            @param _class: the HTML class (this is added to layout classes)
            @param _title: the HTML title
            @param _type: the HTML type
            @param _value: the HTML value
            @param _target: the HTML target

            @param layout: custom rendering function. Default layout is a
                   standard button on a full web page.
                   Current alternate options are:
                   S3Button.layout_action: for "action buttons", i.e. buttons
                       that will be included on each element in a list. (These
                       will have "[id]" in place of an individual record id in
                       their args.)
                   S3Button.layout_dl: for a button on an item in a datalist or
                       on the border of a widget containing a datalist

            @param attributes: any other attributes used by the layout

            Additional parameters for specific formats and methods:
            
            Standard CRUD buttons may have:
            @param custom: a custom button rendered as a Web2py HTML helper.
                   The only alteration will be to add bootstrap classes if
                   needed.

            A datalist edit button requires:
            @param listid: the listid (HTML id property of the datalist that
                   contains this item), or "datalist".
                   The URL var "refresh" will be set to the value of listid.
                   If this is not "datalist", then "record": id is also
                   included in the URL vars.
        """

        # @ToDo: Clean up anything sending in alternate names for crud methods
        # then get rid of this?
        if m in self.ACTION_METHOD:
            m = self.ACTION_METHOD[m]

        return super(S3Button, self).__init__(a=a, c=c, f=f, t=t, m=m, p=p,
                                              id=id,
                                              extension=extension,
                                              args=args,
                                              vars=vars,
                                              r=r,
                                              url=url,
                                              label=label,
                                              tooltip=tooltip,
                                              icon=icon,
                                              format=format,
                                              custom=custom,
                                              layout=layout_method,
                                              _id=_id,
                                              _name=_name,
                                              _class=_class,
                                              _type=_type,
                                              _value=_value,
                                              _title=_title,
                                              _target=_target,
                                              **attributes
                                             )


    # -------------------------------------------------------------------------
    @staticmethod
    def crud_string(item):
        """ Get appropriate crud string or substitute """

        S3CRUD = current.manager.S3CRUD

        crud_str = ""
        crud_name = item.crud_name
        method = item.method
        tablename = item.tablename
        if not crud_name and method:
            crud_name = S3Button.CRUD_NAMES.get(method, None)
        if crud_name and tablename:
            crud_str = S3CRUD.crud_string(item.tablename, crud_name)
        if not crud_str:
            crud_str = item.label
        elif method:
            crud_str = T(method)

        return crud_str

    # -------------------------------------------------------------------------
    # @ToDo: It would be much better were this done where the user's access is
    # known, namely, in S3NavigationItem.__init__.

    @staticmethod
    def style_method(item):
        """
            Infer method if not specified, for selecting style elements

            If this is a request for a resource without a method, it will turn
            into a read / update if it has a specific id, or list if not.

            The purpose of this is to get a better default for icons, etc.,
            in this very common case. This is *not* to be used for the method
            in the href.
        """

        if item.method:
            return item.method

        # It is only appropriate to default the method when the request is
        # for a resource, rather than for a custom function.
        # @ToDo: Verify that S3NavigationItem.__init__ does not set this
        # unless c and f are for an existing table.
        if not item.tablename:
            return S3Button.NOMETHOD

        # @ToDo: Could S3NavigationItem.__init__ determine whether the user
        # will get read or update access to a specific record, and leave a
        # breadcrumb so we could use the proper icon?
        DEFAULT_METHOD = {True: LIST,
                          False: UPDATE}
        return DEFAULT_METHOD[item.id is None]
            
    # -------------------------------------------------------------------------
    @staticmethod
    def layout(item):
        """
            Layout for a standard CRUD or action button

            On permission failure, returns "" for the convenience of the caller.
        """

        if not item.authorized:
            return ""

        bootstrap = current.response.s3.crud.formstyle == "bootstrap"

        attr = item.attr
        opts = item.opts

        # Custom button?
        custom = attr.custom
        if custom and bootstrap and hasattr(custom, "add_class"):
            custom.add_class(S3Button.BOOTSTRAP_PRIMARY)
            return custom

        custom_class = opts.get("_class", "")
        _class = "%s %s" % (S3Button.ACTION_BUTTON, custom_class)
        # @ToDo: Is this a misuse of bootstrap btn-primary? It is supposed to
        # go in one main / emphasized button in a set of buttons, no?)
        if bootstrap:
            _class = "%s %s" % (_class, S3Button.BOOTSTRAP_PRIMARY)

        label = item.label
        if not label:
            label = S3Button.crud_string(item)

        _href = opts._href
        if not _href:
            _href=item.url()
        button = A(label,
                   _id=opts._id,
                   _class=_class,
                   _href=_href,
                   _title=opts._title,
                   _target=opts._target,
                   _role="button",
                  )

        title = item.title
        tooltip = item.tooltip
        if tooltip is not None:
            if title is None:
                title = label
            ttip = DIV(_class="tooltip",
                       _title="%s|%s" % (title, tooltip))
            button = DIV(button, ttip)

        return button

    # -------------------------------------------------------------------------
    @staticmethod
    def layout_dl(item):
        """
            Layout for a CRUD or action button in datalist format

            Typically these will be either edit or delete buttons for datalist
            item thumbnails on cards, or an add button on the datalist container
            widget.
            
            A datalist button is typically small, so currently uses only an icon
            with no label. For the tooltip, a supplied tooltip will be used if
            any, else the label, else the crud string for the supplied
            crud_name, else the crud string associated with the method.
    
            The following should be provided
            @param c: controller
            @param f: function
            @param m: method: See the DL_BUTTON_* tables above for which methods
                      currently have default icons, etc. Add to said tables to
                      include more methods.
            @param t: table name (alternative to c, f)
            @param r: request (alternative to c, f, m)
            @param id: id of record to edit (not needed for delete)
            @param listid: value of refresh var, typically the listid (HTML id
                   property of the containing list) or "datalist" -- if not
                   "datalist", then "record": id is also included in vars
            @param vars: any extra vars besides record and refresh.

            See optional params in S3Button.__init__.

            On permission or other failure, returns "" for the convenience of
            the caller.
        """

        if not item.authorized:
            return ""

        s3 = current.response.s3
        crud = s3.crud
        S3CRUD = current.manager.S3CRUD
        bootstrap = crud.formstyle == "bootstrap"

        attr = item.attr
        opts = item.opts
        vars = attr.vars
        method = item.method
        style_method = S3Button.style_method(item)

        listid = item.listid
        if listid:
            vars["refresh"] = listid
            if listid != "datalist":
                vars["record"] = id

        label = item.label
        if not label:
            label = S3Button.crud_string(item)

        tooltip = item.tooltip
        if not tooltip:
            tooltip = label

        icon = item.icon
        if not icon:
            icon = S3Button.DL_BUTTON_ICON.get(style_method, None)
        if icon:
            label = I(" ", _class="icon %s" % icon)

        dl_class = S3Button.DL_BUTTON_CLASS.get(style_method, "")
        custom_class = opts.get("_class", "")
        _class = "%s %s" % (dl_class, custom_class)
        if bootstrap:
            b_class = S3Button.DL_BUTTON_BOOTSTRAP.get(style_method, "")
            _class = "%s %s" % (_class, b_class)

        # Delete is a special case, handled from the client, as it must
        # remove the card from its container.
        if method == DELETE:
            _href = None

        else:
            _href = opts._href
            if not _href:
                arg = S3Button.DL_BUTTON_ARG.get(style_method, None)
                if not arg:
                    # Unsupported datalist button type.
                    return ""
                _href = URL(c=c, f=f,
                            args=[id, arg],
                            vars=vars)

        btn = A(label,
                _href=_href,
                _class=_class,
                _title=tooltip,
                _role="button",
               )

        return btn

# END =========================================================================
