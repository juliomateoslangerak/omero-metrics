class OmeroAuth:
    """Django-plotly-dash expects request.user to be set"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # code before response is handled goes here
        request.user = "OMERO User"
        response = self.get_response(request)
        return response
