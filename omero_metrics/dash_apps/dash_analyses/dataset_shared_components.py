import dash_mantine_components as dmc
from dash import dcc, html, dependencies

# COMPONENTS
def notification_provider():
    return dmc.NotificationProvider(position="top-center")


def notifications_container():
    return html.Div(id="notifications_container")


def confirm_delete_modal():
    return dmc.Modal(
        title="Confirm Delete",
        id="confirm-delete-modal",
        children=[
            dmc.Text("Are you sure you want to delete this dataset outputs?"),
            dmc.Space(h=20),
            dmc.Group(
                [
                    dmc.Button(
                        "Delete",
                        id="confirm-delete-button",
                        color="red",
                    ),
                    dmc.Button(
                        "Cancel",
                        id="cancel-delete-button",
                        color="gray",
                        variant="outline",
                    ),
                ],
                justify="flex-end",
            ),
        ],
    )



# # CALLBACKS
# @omero_dataset_psf_beads.expanded_callback(
#     dependencies.Output("confirm_delete", "opened"),
#     dependencies.Output("notifications_container", "children"),
#     dependencies.Output("modal-submit-button", "loading"),
#     [
#         dependencies.Input("delete_data", "n_clicks"),
#         dependencies.Input("modal-submit-button", "n_clicks"),
#         dependencies.Input("modal-close-button", "n_clicks"),
#         dependencies.State("confirm_delete", "opened"),
#     ],
#     prevent_initial_call=True,
# )
# def delete_dataset(*args, **kwargs):
#     triggered_button = kwargs["callback_context"].triggered[0]["prop_id"]
#     dataset_id = kwargs["session_state"]["context"][
#         "mm_dataset"
#     ].data_reference.omero_object_id
#     request = kwargs["request"]
#     opened = not args[3]
#     if triggered_button == "modal-submit-button.n_clicks" and args[0] > 0:
#         sleep(1)
#         response_type, response_msg = views.delete_dataset(
#             request, dataset_id=dataset_id
#         )
#
#         return my_components.notification_handler(
#             response_type, response_msg, opened
#         )
#     else:
#         return opened, None, False
