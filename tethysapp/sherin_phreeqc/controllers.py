import sys
sys.path.append('/usr/local/lib/python2.7/dist-packages')

from tethys_gizmos.gizmo_options import MapView, MVView
from tethys_sdk.gizmos import Button, SelectInput,DatePicker
from django.shortcuts import render


def home(request):
    """
    Controller for the app home page.
    """
    # Define initial view for Map View
    view_options = MVView(
        projection='EPSG:4326',
        center=[-100, 40],
        zoom=3.5,
        maxZoom=18,
        minZoom=2
    )

    # Configure the map
    map_options = MapView(height='500px',
                          width='100%',
                          view=view_options,
                          legend=False)


     # Pre-populate lat-picker and lon_picker from model
    select_basemap = SelectInput(display_text='Basemap',
                            name='select_basemap',
                            multiple=False,
                            options=[('Bing', 'bing_layer'), ('OpenStreet', 'openstreet_layer')],
                            original=['Bing'],
                            attributes="id=select_basemap onchange=run_select_basemap()")

    select_site = SelectInput(display_text='Sites',
                            name='select_site',
                            multiple=True,
                            options=[('LR_Mendon_AA', 'LR_Mendon_AA_layer'), ('LR_Mainstreet_BA', 'LR_Mainstreet_BA_layer'), ('LR_WaterLab_AA', 'LR_WaterLab_AA_layer'), ('LR_TG_BA', 'LR_TG_BA_layer'), ('LR_FB_BA', 'LR_FB_BA_layer')],
                            attributes="id=select_site onchange=run_select_site()")

    date_picker = DatePicker(name='date1',
                         display_text='Date',
                         autoclose=True,
                         format='MM d, yyyy',
                         start_date='1/1/2010',
                         start_view='decade',
                         today_button=True,
                         initial='January 1, 2014')

    btnSearch = Button(display_text="Search",
                        name="btnSearch",
                        attributes="id=btnSearch onclick=run_search_results();",
                        submit=False)

    btnPhreeqc = Button(display_text="Run Phreeqc",
                        name="btnPhreeqc",
                        attributes="id=btnPhreeqc onclick=run_phreeqc_analyze();",
                        submit=False)

    # Pass variables to the template via the context dictionary
    context = {'map_options': map_options,
               'select_basemap': select_basemap,
               'select_site': select_site,
               'btnSearch': btnSearch,
               'date_picker': date_picker,
               'btnPhreeqc':btnPhreeqc,
               }
    return render(request, 'sherin_phreeqc/home.html', context)
