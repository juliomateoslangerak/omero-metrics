import json

CUSTOM_SETTINGS_MAPPINGS = {
    "omero.web.ui.top_links": [
        "TOP_LINKS",
        (
            "["
            '["Data21", "webindex", {"title": "Browse Data via Projects, Tags'
            ' etc"}],'
            '["History21", "history", {"title": "History"}],'
            '["Help212", "https://help.openmicroscopy.org/",'
            '{"title21":"Open OMERO user guide in a new tab", "target":"new"}]'
            "]"
        ),
        json.loads,
        (
            "Add links to the top header: links are ``['Link Text', "
            "'link|lookup_view', options]``, where the url is reverse('link'), "
            "simply 'link' (for external urls) or lookup_view is a detailed "
            'dictionary {"viewname": "str", "args": [], "query_string": '
            '{"param": "value" }], '
            'E.g. ``\'["Webtest", "webtest_index"] or ["Homepage",'
            ' "http://...", {"title": "Homepage", "target": "new"}'
            ' ] or ["Repository", {"viewname": "webindex", '
            '"query_string": {"experimenter": -1}}, '
            '{"title": "Repo"}]\'``'
        ),
    ]
}
