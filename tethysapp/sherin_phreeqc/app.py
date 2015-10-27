from tethys_sdk.base import TethysAppBase, url_map_maker


class Sherin(TethysAppBase):
    """
    Tethys app class for Sherin.
    """

    name = 'Sherin Phreeqc'
    index = 'sherin_phreeqc:home'
    icon = 'sherin_phreeqc/images/index.png'
    package = 'sherin_phreeqc'
    root_url = 'sherin-phreeqc'
    color = '#34495e'
        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='sherin-phreeqc',
                           controller='sherin_phreeqc.controllers.home'),
        )

        return url_maps