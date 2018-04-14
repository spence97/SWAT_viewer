from tethys_sdk.base import TethysAppBase, url_map_maker


class swat(TethysAppBase):
    """
    Tethys app class for SWAT.
    """

    name = 'SWAT Output Viewer - Mekong'
    index = 'swat:home'
    icon = 'swat/images/swat_clipart.png'
    package = 'swat'
    root_url = 'swat'
    color = '#060087'
    description = 'Place a brief description of your app here.'
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='swat/home',
                controller='swat.controllers.home'
            ),
            UrlMap(
                name='time-series',
                url='swat/timeseries',
                controller='swat.controllers.timeseries'
            )
        )

        return url_maps
