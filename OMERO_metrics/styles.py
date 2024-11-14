THEME = {
    "primary": "#189A35",
    "primary_light": "#1FB344",
    "secondary": "#63aa47",
    "accent": "#14b8a6",
    "background": "#ffffff",
    "surface": "#f8f9fa",
    "border": "#e9ecef",
    "text": {
        "primary": "#2C3E50",
        "secondary": "#6c757d",
    },
    "error": "#ef4444",
    "warning": "#f59e0b",
    "success": "#10B981",
}


TAB_STYLES = {
    "tab": {
        "fontSize": "14px",
        "fontWeight": 500,
        "height": "40px",
        "borderRadiusBottom": "6px",
        "backgroundColor": "white",
        "&[data-active]": {
            "backgroundColor": THEME["primary_light"],
            "color": THEME["primary"],
        },
    }
}

TAB_ITEM_STYLE = {
    "fontSize": "1.1rem",
    "fontWeight": "bold",
    "color": THEME["primary"],
    "backgroundColor": "#e2ffe2",
}


INPUT_STYLES = {
    "rightSection": {"pointerEvents": "none"},
    "item": {"fontSize": "14px"},
    "input": {"borderColor": THEME["primary"]},
    "label": {"marginBottom": "8px"},
}

TABLE_MANTINE_STYLE = {
    "backgroundColor": "#e2ffe2",
    "width": "98%",
    "height": "auto",
    "margin": "5px",
    "borderRadius": "0.5rem",
    "align": "center",
}
TABLE_STYLE = {
    "overflowX": "auto",
    "borderRadius": "0.5rem",
    "fontFamily": "'Arial', 'Helvetica', sans-serif",
    "borderCollapse": "collapse",
    "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
    "margin": "20px 0",
    "borderLeft": "none",
    "borderRight": "none",
}

TABLE_CELL_STYLE = {
    "whiteSpace": "normal",
    "height": "30px",
    "minWidth": "100px",
    "width": "100px",
    "maxWidth": "100px",
    "textAlign": "left",
    "textOverflow": "ellipsis",
    "fontSize": "12px",
    "fontFamily": "'Arial', 'Helvetica', sans-serif",
    "color": "#333",
    "fontWeight": "500",
    "padding": "10px",
    "border": "1px solid #ddd",
    "borderLeft": "none",
    "borderRight": "none",
}

TABLE_HEADER_STYLE = {
    "backgroundColor": THEME["primary"],
    "fontWeight": "bold",
    "fontSize": "16px",
    "paddingTop": "12px",
    "paddingBottom": "12px",
    "color": THEME["surface"],
    "border": "1px solid #ddd",
    "borderLeft": "none",
    "borderRight": "none",
}

STYLE_DATA_CONDITIONAL = (
    [
        {
            "if": {"row_index": "odd"},
            "backgroundColor": THEME["background"],
        },
        {
            "if": {"row_index": "even"},
            "backgroundColor": THEME["surface"],
        },
    ],
)

PAPER_STYLE = {
    "width": "100%",
    "maxWidth": "600px",
    "margin": "auto",
}

FIELDSET_STYLE = {
    "padding": "10px",
    "margin": "10px",
}


INPUT_BASE_STYLES = {
    "wrapper": {
        "height": "40px",
    },
    "input": {
        "height": "40px",
        "minHeight": "40px",
        "lineHeight": "40px",  # Match height for vertical centering
        "padding": "0 12px",  # Consistent padding
        "display": "flex",
        "alignItems": "center",  # Center content vertically
        "borderColor": THEME["primary"],
        "fontSize": "14px",
    },
    "rightSection": {
        "pointerEvents": "none",
        "height": "40px",
        "display": "flex",
        "alignItems": "center",  # Center icons vertically
    },
    "leftSection": {
        "height": "40px",
        "display": "flex",
        "alignItems": "center",  # Center icons vertically
    },
    "label": {
        "marginBottom": "8px",
        "fontSize": "14px",
        "fontWeight": 500,
    },
    "item": {
        "fontSize": "14px",
    },
}

SELECT_STYLES = {
    **INPUT_BASE_STYLES,
    "dropdown": {
        "borderRadius": "6px",
        "border": f'1px solid {THEME["border"]}',
    },
    "input": {
        **INPUT_BASE_STYLES["input"],
        "paddingLeft": "36px",  # Adjust for icon
    },
}

DATEPICKER_STYLES = {
    **INPUT_BASE_STYLES,
    "calendar": {
        "borderRadius": "6px",
        "border": f'1px solid {THEME["border"]}',
    },
    "input": {
        **INPUT_BASE_STYLES["input"],
        "paddingLeft": "36px",  # Adjust for icon
    },
}

CARD_STYLE = {
    "backgroundColor": THEME["surface"],
    "borderRadius": "8px",
    "border": f'1px solid {THEME["border"]}',
    "padding": "24px",
    "height": "100%",
    "boxShadow": "0 1px 3px 0 rgb(0 0 0 / 0.1)",
}

CARD_STYLE1 = {
    "backgroundColor": "white",
    "borderRadius": "8px",
    "border": f'1px solid {THEME["border"]}',
    "padding": "24px",
    "height": "100%",
    "boxShadow": "0 1px 3px 0 rgb(0 0 0 / 0.1)",
}

BUTTON_STYLE = {
    "backgroundColor": THEME["primary"],
    "color": "white",
    "fontSize": "14px",
    "fontWeight": 500,
    "height": "40px",
    "padding": "0 16px",
    "borderRadius": "6px",
}

MANTINE_THEME = {
    "colorScheme": "light",
    "primaryColor": "green",
    "components": {
        "Button": {"styles": {"root": {"fontWeight": 500}}},
        "Select": {"styles": SELECT_STYLES},
        "DatePicker": {"styles": DATEPICKER_STYLES},
        "Input": {"styles": INPUT_STYLES},
        "Paper": {"defaultProps": {"withBorder": True}},
        "Card": {
            "styles": {"root": {"borderRadius": "8px"}},
        },
        "Title": {"styles": {"root": {"letterSpacing": "-0.5px"}}},
        "Alert": {"styles": {"root": {"borderRadius": "8px"}}},
    },
}


CONTAINER_STYLE = {
    "backgroundColor": THEME["surface"],
    "margin": "10px",
    "borderRadius": "0.5rem",
    "padding": "10px",
}

HEADER_PAPER_STYLE = {
    "shadow": "sm",
    "p": "md",
    # "radius": "lg",
    "mb": "md",
}

CONTENT_PAPER_STYLE = {
    "shadow": "xs",
    "p": "md",
    "radius": "md",
    "h": "100%",
}

GRAPH_STYLE = {
    "height": "300px",
}

PLOT_LAYOUT = {
    "margin": dict(l=40, r=40, t=40, b=40),
    "plot_bgcolor": THEME["background"],
    "paper_bgcolor": THEME["background"],
    "xaxis_showgrid": False,
    "yaxis_showgrid": False,
    "xaxis_zeroline": False,
    "yaxis_zeroline": False,
}


LINE_CHART_SERIES = [
    {"name": "Diagonal (↘)", "color": "violet.9"},
    {"name": "Diagonal (↗)", "color": "blue.9"},
    {"name": "Horizontal (→)", "color": "pink.9"},
    {"name": "Vertical (↓)", "color": "teal.9"},
]
