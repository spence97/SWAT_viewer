from tethys_sdk.base import TethysAppBase, url_map_maker


class swat(TethysAppBase):
    """
    Tethys app class for SWAT.
    """

    name = 'SWAT Data Viewer'
    index = 'swat:home'
    icon = 'swat/images/logo2.png'
    package = 'swat'
    root_url = 'swat'
    color = '#2c3e50'
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
                name='get-upstream',
                url='swat/get_upstream',
                controller='swat.ajax_controllers.get_upstream'
            ),
            UrlMap(
                name='save_json',
                url='swat/save_json',
                controller='swat.ajax_controllers.save_json'
            ),
            UrlMap(
                name='run_nasaaccess',
                url='swat/run_nasaaccess',
                controller='swat.ajax_controllers.run_nasaaccess'
            ),
            UrlMap(
                name='lulc_compute',
                url='swat/lulc_compute',
                controller='swat.ajax_controllers.lulc_compute'
            ),
            UrlMap(
                name='time-series',
                url='swat/timeseries',
                controller='swat.ajax_controllers.timeseries'
            ),
            UrlMap(
                name='add_watershed',
                url='swat/add_watershed',
                controller='swat.controllers.add_watershed'
            ),
            UrlMap(
                name='upload_files',
                url='swat/upload',
                controller='swat.ajax_controllers.upload_files'
            ),
            UrlMap(
                name='download_csv',
                url='swat/download_csv',
                controller='swat.ajax_controllers.download_csv'
            ),
            UrlMap(
                name='download_ascii',
                url='swat/download_ascii',
                controller='swat.ajax_controllers.download_ascii'
            )

        )

        return url_maps
