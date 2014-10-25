# -*- coding: utf-8 -*-

try:
    # Python 2.7
    from collections import OrderedDict
except:
    # Python 2.6
    from gluon.contrib.simplejson.ordered_dict import OrderedDict

from gluon import current
from gluon.storage import Storage

T = current.T
settings = current.deployment_settings

"""
    Template settings for an Incident Response System

    Initially targeting Sierra Leone, but easily adapatable for other locations
"""

settings.base.system_name = T("Sierra Leone Incident Response System")
settings.base.system_name_short = T("SL IRS")

# PrePopulate data
settings.base.prepopulate = ("IRS", "default/users")

# Theme (folder to use for views/layout.html)
settings.base.theme = "IRS"

# Authentication settings
# Should users be allowed to register themselves?
#settings.security.self_registration = False
# Do new users need to verify their email address?
settings.auth.registration_requires_verification = True
# Do new users need to be approved by an administrator prior to being able to login?
#settings.auth.registration_requires_approval = True
#settings.auth.registration_requests_organisation = True

# Approval emails get sent to all admins
settings.mail.approver = "ADMIN"

# Restrict the Location Selector to just certain countries
# NB This can also be over-ridden for specific contexts later
# e.g. Activities filtered to those of parent Project
settings.gis.countries = ("SL",)

# L10n settings
# Languages used in the deployment (used for Language Toolbar & GIS Locations)
# http://www.loc.gov/standards/iso639-2/php/code_list.php
settings.L10n.languages = OrderedDict([
#    ("ar", "العربية"),
#    ("bs", "Bosanski"),
    ("en_gb", "English"),
#    ("fr", "Français"),
#    ("de", "Deutsch"),
#    ("el", "ελληνικά"),
#    ("es", "Español"),
#    ("it", "Italiano"),
#    ("ja", "日本語"),
#    ("km", "ភាសាខ្មែរ"),
#    ("ko", "한국어"),
#    ("ne", "नेपाली"),          # Nepali
#    ("prs", "دری"), # Dari
#    ("ps", "پښتو"), # Pashto
#    ("pt", "Português"),
#    ("pt-br", "Português (Brasil)"),
#    ("ru", "русский"),
#    ("tet", "Tetum"),
#    ("tl", "Tagalog"),
#    ("ur", "اردو"),
#    ("vi", "Tiếng Việt"),
#    ("zh-cn", "中文 (简体)"),
#    ("zh-tw", "中文 (繁體)"),
])
# Default language for Language Toolbar (& GIS Locations in future)
settings.L10n.default_language = "en_gb"
# Uncomment to Hide the language toolbar
settings.L10n.display_toolbar = False
# Default timezone for users
#settings.L10n.utc_offset = "UTC +0100"

# Security Policy
# http://eden.sahanafoundation.org/wiki/S3AAA#System-widePolicy
# 1: Simple (default): Global as Reader, Authenticated as Editor
# 2: Editor role required for Update/Delete, unless record owned by session
# 3: Apply Controller ACLs
# 4: Apply both Controller & Function ACLs
# 5: Apply Controller, Function & Table ACLs
# 6: Apply Controller, Function, Table ACLs and Entity Realm
# 7: Apply Controller, Function, Table ACLs and Entity Realm + Hierarchy
# 8: Apply Controller, Function, Table ACLs, Entity Realm + Hierarchy and Delegations
#
settings.security.policy = 7 # Organisation-ACLs

# =============================================================================
# Project Settings
# Uncomment this to use settings suitable for a global/regional organisation (e.g. DRR)
settings.project.mode_3w = True
# Uncomment this to use Codes for projects
settings.project.codes = True
# Uncomment this to enable Hazards in 3W projects
#settings.project.hazards = True
# Uncomment this to use multiple Budgets per project
#settings.project.multiple_budgets = True
# Uncomment this to use multiple Organisations per project
settings.project.multiple_organisations = True
# Uncomment this to enable Themes in 3W projects
#settings.project.themes = True
# Uncomment this to customise
# Links to Filtered Components for Donors & Partners
#settings.project.organisation_roles = {
#    1: T("Lead Organization"),
#    2: T("Partner Organization"),
#    3: T("Donor"),
#    #4: T("Customer"), # T("Beneficiary")?
#    #5: T("Supplier"),
#    9: T("Partner Organization"), # Needed for IFRC RMS interop ("Partner National Society")
#}

# =============================================================================
# Requests
#settings.req.use_commit = False
# Restrict the type of requests that can be made, valid values in the
# list are ["Stock", "People", "Other"]. If this is commented out then
# all types will be valid.
settings.req.req_type = ["Stock"]

# -----------------------------------------------------------------------------
def customise_hms_hospital_resource(r, tablename):

    if r.representation == "geojson":
        # Don't represent the facility_status as numbers are smaller to xmit
        current.s3db.hms_status.facility_status.represent = None
        return

    hms_facility_status_opts = {
        #1: T("Normal"),
        1: T("Functioning"),
        #2: T("Compromised"),
        #3: T("Evacuating"),
        4: T("Closed"),
        5: T("Pending"),
        #99: T("No Response")
    }

    from gluon import IS_EMPTY_OR, IS_IN_SET

    s3db = current.s3db
    NONE = current.messages["NONE"]

    field = s3db.hms_status.facility_status
    field.represent = lambda opt: hms_facility_status_opts.get(opt, NONE)
    field.requires = IS_EMPTY_OR(IS_IN_SET(hms_facility_status_opts))

settings.customise_hms_hospital_resource = customise_hms_hospital_resource

# -----------------------------------------------------------------------------
def customise_stats_demographic_data_resource(r, tablename):

    s3db = current.s3db
    table = s3db.stats_demographic_data

    # Add a Timeplot tab to summary page
    # @ToDo: Widget version of timeplot
    #settings.ui.summary = list(settings.ui.summary) + {"name": "timeplot",
    #                                                   "label": "TimePlot",
    #                                                   "widgets": [{"method": "timeplot", "ajax_init": True}],
    #                                                   }

    from s3 import S3OptionsFilter, S3LocationFilter
    filter_widgets = [S3OptionsFilter("parameter_id",
                                      label = T("Type"),
                                      multiple = False,
                                      # Not translateable
                                      #represent = "%(name)s",
                                      ),
                      # @ToDo: 'Month' &/or Week VF
                      #S3OptionsFilter("month",
                      #                #multiple = False,
                      #                operator = "anyof",
                      #                options = lambda: \
                      #                  stats_month_options("stats_demographic_data"),
                      #                ),
                      ]
    
    if r.method != "timeplot":
        # This is critical for the Map, but breaks aggregated Report data
        filter_widgets.append(S3OptionsFilter("location_id$level",
                                              label = T("Level"),
                                              multiple = False,
                                              # Not translateable
                                              #represent = "%(name)s",
                                              ))
    filter_widgets.append(S3LocationFilter("location_id"))

    # Sum doesn't make sense for data which is already cumulative
    #report_options = s3db.get_config(tablename, "report_options")
    #report_options.fact = [(T("Value"), "max(value)")]
    #report_options.defaults.fact = "max(value)"

    #report_options = Storage(rows = location_fields + ["month"],
    #                         cols = ["parameter_id"],
    #                         fact = [(T("Value"), "max(value)"),
    #                                 ],
    #                         defaults = Storage(rows = "location_id",
    #                                            cols = "parameter_id",
    #                                            fact = "max(value)",
    #                                            totals = True,
    #                                            chart = "breakdown:rows",
    #                                            table = "collapse",
    #                                            )
    #                         )

    #s3db.configure(tablename,
    #               filter_widgets = filter_widgets,
    #               report_options = report_options,
    #               )

settings.customise_stats_demographic_data_resource = customise_stats_demographic_data_resource

# -----------------------------------------------------------------------------
# Comment/uncomment modules here to disable/enable them
# Modules menu is defined in modules/eden/menu.py
settings.modules = OrderedDict([
    # Core modules which shouldn't be disabled
    ("default", Storage(
        name_nice = T("Home"),
        restricted = False, # Use ACLs to control access to this module
        access = None,      # All Users (inc Anonymous) can see this module in the default menu & access the controller
        module_type = None  # This item is not shown in the menu
    )),
    ("admin", Storage(
        name_nice = T("Administration"),
        #description = "Site Administration",
        restricted = True,
        access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
        module_type = None  # This item is handled separately for the menu
    )),
    ("appadmin", Storage(
        name_nice = T("Administration"),
        #description = "Site Administration",
        restricted = True,
        module_type = None  # No Menu
    )),
    ("errors", Storage(
        name_nice = T("Ticket Viewer"),
        #description = "Needed for Breadcrumbs",
        restricted = False,
        module_type = None  # No Menu
    )),
    #("sync", Storage(
    #    name_nice = T("Synchronization"),
    #    #description = "Synchronization",
    #    restricted = True,
    #    access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
    #    module_type = None  # This item is handled separately for the menu
    #)),
    #("tour", Storage(
    #    name_nice = T("Guided Tour Functionality"),
    #    module_type = None,
    #)),
    #("translate", Storage(
    #    name_nice = T("Translation Functionality"),
    #    #description = "Selective translation of strings based on module.",
    #    module_type = None,
    #)),
    ("gis", Storage(
        name_nice = T("Map"),
        #description = "Situation Awareness & Geospatial Analysis",
        restricted = True,
        module_type = 1,     # 1st item in the menu
    )),
    ("pr", Storage(
        name_nice = T("Person Registry"),
        #description = "Central point to record details on People",
        restricted = True,
        access = "|1|",     # Only Administrators can see this module in the default menu (access to controller is possible to all still)
        module_type = 10
    )),
    ("org", Storage(
        name_nice = T("Organizations"),
        #description = 'Lists "who is doing what & where". Allows relief agencies to coordinate their activities',
        restricted = True,
        module_type = 10
    )),
    ("hrm", Storage(
        name_nice = T("Staff"),
        #description = "Human Resources Management",
        restricted = True,
        module_type = 3,
    )),
    #("vol", Storage(
    #    name_nice = T("Volunteers"),
    #    #description = "Human Resources Management",
    #    restricted = True,
    #    module_type = 2,
    #)),
    ("cms", Storage(
      name_nice = T("Content Management"),
      #description = "Content Management System",
      restricted = True,
      module_type = 10,
    )),
    ("doc", Storage(
        name_nice = T("Documents"),
        #description = "A library of digital resources, such as photos, documents and reports",
        restricted = True,
        module_type = 10,
    )),
    ("msg", Storage(
        name_nice = T("Messaging"),
        #description = "Sends & Receives Alerts via Email & SMS",
        restricted = True,
        # The user-visible functionality of this module isn't normally required. Rather it's main purpose is to be accessed from other modules.
        module_type = None,
    )),
    ("event", Storage(
        name_nice = T("Events"),
        #description = "Activate Events (e.g. from Scenario templates) for allocation of appropriate Resources (Human, Assets & Facilities).",
        restricted = True,
        module_type = 2,
    )),
    # Specific for Sierrra Leone:
    ("disease", Storage(
        name_nice = T("Disease"),
        restricted = True,
        module_type = 10
    )),
    ("hms", Storage(
        name_nice = T("Hospitals"),
        #description = "Helps to monitor status of hospitals",
        restricted = True,
        module_type = 10
    )),
    ("dvi", Storage(
        name_nice = T("Burials"),
        restricted = True,
        module_type = 10
    )),
    ("supply", Storage(
        name_nice = T("Supply Chain Management"),
        #description = "Used within Inventory Management, Request Management and Asset Management",
        restricted = True,
        module_type = None, # Not displayed
    )),
    ("asset", Storage(
        name_nice = T("Assets"),
        #description = "Recording and Assigning Assets",
        restricted = True,
        module_type = None, # Just used for Vehicles
    )),
    # Vehicle depends on Assets
    ("vehicle", Storage(
        name_nice = T("Vehicles"),
        #description = "Manage Vehicles",
        restricted = True,
        module_type = 4,
    )),
    # Enable for org_resource?
    ("stats", Storage(
        name_nice = T("Statistics"),
        #description = "Manages statistics",
        restricted = True,
        module_type = 10,
    )),
    ("transport", Storage(
       name_nice = T("Transport"),
       restricted = True,
       module_type = 10,
    )),
    # Enabled as-requested by user
    ("inv", Storage(
        name_nice = T("Warehouses"),
        #description = "Receiving and Sending Items",
        restricted = True,
        module_type = 4
    )),
    ("req", Storage(
        name_nice = T("Requests"),
        #description = "Manage requests for supplies, assets, staff or other resources. Matches against Inventories where supplies are requested.",
        restricted = True,
        module_type = 10,
    )),
    ("project", Storage(
        name_nice = T("Projects"),
        #description = "Tracking of Projects, Activities and Tasks",
        restricted = True,
        module_type = 2
    )),
    #("cr", Storage(
    #    name_nice = T("Shelters"),
    #    #description = "Tracks the location, capacity and breakdown of victims in Shelters",
    #    restricted = True,
    #    module_type = 10
    #)),
    #("dvr", Storage(
    #   name_nice = T("Disaster Victim Registry"),
    #   #description = "Allow affected individuals & households to register to receive compensation and distributions",
    #   restricted = True,
    #   module_type = 10,
    #)),
])
