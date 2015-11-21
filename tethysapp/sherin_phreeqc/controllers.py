import sys
import shutil
import traceback
import matplotlib.pyplot as plt
from suds.client import Client
from pandas import Series
import logging
logging.getLogger('suds.client').setLevel(logging.CRITICAL)
sys.path.append('/usr/local/lib/python2.7/dist-packages')
from django.shortcuts import render
from django.http import JsonResponse
from tethys_gizmos.gizmo_options import MapView, MVView
from tethys_sdk.gizmos import Button, SelectInput, DatePicker, TimeSeries



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
                            options=[('LR_Mendon_AA', 'LR_Mendon_AA'), ('LR_Mainstreet_BA', 'LR_Mainstreet_BA'),
                                     ('LR_WaterLab_AA', 'LR_WaterLab_AA'), ('LR_TG_BA', 'LR_TG_BA'), ('LR_FB_BA', 'LR_FB_BA'),
                                     ('PR_BI_AA', 'PR_BI_AA'), ('PR_CH_AA', 'PR_CH_AA'), ('PR_LM_AA', 'PR_LM_AA'),('PR_ST_AA', 'PR_ST_AA'),
                                     ('RB_ARBR_AA', 'RB_ARBR_AA'), ('RB_CG_BA', 'RB_CG_BA'), ('RB_FD_AA', 'RB_FD_AA'), ('RB_RBG_BA', 'RB_RBG_BA'), ('RB_KF_BA', 'RB_KF_BA')],
                            attributes="id=select_site onchange=run_select_site()")

    begin_date = DatePicker(name='begin_date',
                         display_text='Begin Date',
                         autoclose=True,
                         format='yyyy-mm-dd',
                         start_date='2010-01-01',
                         start_view='decade',
                         today_button=True,
                         initial='2015-03-01')

    end_date = DatePicker(name='end_date',
                         display_text='End Date',
                         autoclose=True,
                         format='yyyy-mm-dd',
                         start_date='2010-01-01',
                         start_view='decade',
                         today_button=True,
                         initial='2015-03-11')

    btnSearch = Button(display_text="Search",
                        name="btnSearch",
                        attributes="id=btnSearch onclick=run_search_results();",
                        submit=False)

    btnPhreeqc = Button(display_text="Run Phreeqc",
                        name="btnPhreeqc",
                        attributes="id=btnPhreeqc onclick=run_phreeqc_analyze();",
                        submit=False)


    line_plot_view = TimeSeries(
                height='500px',
                width='500px',
                engine='highcharts',
                title='iUTAH GAMUT DATA',
                subtitle='Temperature,DO,pH,and Nitrate-N',
                y_axis_title='Value',
                series=[
                   {
                       'name': 'pH',
                       'color': '#0066ff',
                       'marker': {'enabled': False},
                       'data': [ ]
                   },
                    {
                       'name': 'Temperature',
                       'color': '#ff6600',
                       'marker': {'enabled': False},
                       'data': [ ]
                   },
                    {
                       'name': 'DO',
                       'color': '#DC143C',
                       'marker': {'enabled': False},
                       'data': [ ]
                   },
                    {
                       'name': 'Nitrate-N',
                       'color': '#9932CC',
                       'marker': {'enabled': False},
                       'data': [ ]
                   }
                ]
            )


    # Pass variables to the template via the context dictionary
    context = {'map_options': map_options,
               'select_basemap': select_basemap,
               'select_site': select_site,
               'btnSearch': btnSearch,
               'begin_date': begin_date,
               'end_date': end_date,
               'btnPhreeqc':btnPhreeqc,
               'line_plot_view': line_plot_view,
               }
    return render(request, 'sherin_phreeqc/home.html', context)


def search_gamut_data(request):
    temp_dir = None

    if request.method == 'GET':
        get_data = request.GET

        siteCodestr = str(get_data['siteCode'])
        beginDate = str(get_data['beginDate'])
        endDate = str(get_data['endDate'])
        # Create the inputs needed for the web service call

        if "LR" in siteCodestr:
            wsdlURL = 'http://data.iutahepscor.org/loganriverwof/cuahsi_1_1.asmx?WSDL'
        elif "PR" in siteCodestr:
            wsdlURL = 'http://data.iutahepscor.org/provoriverwof/cuahsi_1_1.asmx?WSDL'
        else:
            wsdlURL = 'http://data.iutahepscor.org/redbuttecreekwof/cuahsi_1_1.asmx?WSDL'

        siteCode = ':'+ siteCodestr
        variableCode_pH = 'iutah:pH'
        variableCode_Temp = 'iutah:WaterTemp_EXO'
        variableCode_DO = 'iutah:ODO'
        variableCode_N = 'iutah:Nitrate-N'

        print siteCode
        print variableCode_pH
        print variableCode_DO
        print variableCode_N
        print variableCode_Temp
        print beginDate
        print endDate
        print wsdlURL

        # (input future time represent to latest)

        # Create a new object named "NWIS" for calling the web service methods
        # NWIS = Client("http://icewater.usu.edu/MudLake/cuahsi_1_0.asmx?WSDL").service
        # response_pH = NWIS.GetValues("MudLake:USU-ML-Outlet", "MudLake:USU3", "", "", "")
        # print response_pH

        NWIS = Client(wsdlURL).service

        # Call the GetValuesObject method to return datavalues
        response_pH = NWIS.GetValuesObject(siteCode, variableCode_pH, beginDate, endDate,'')

        response_Temp = NWIS.GetValuesObject(siteCode, variableCode_Temp, beginDate, endDate, '')
        response_DO = NWIS.GetValuesObject(siteCode, variableCode_DO, beginDate, endDate, '')
        response_N = NWIS.GetValuesObject(siteCode, variableCode_N, beginDate, endDate, '')

        # Get the site's name from the response
        siteName = response_pH.timeSeries[0].sourceInfo.siteName

        # Create some blank lists in which to put the values and their dates
        a1 = []  # The values
        b1 = []  # The dates
        a2 = []  # The values
        b2 = []  # The dates
        a3 = []  # The values
        b3 = []  # The dates
        a4 = []  # The values
        b4 = []  # The dates

        # Get the values and their dates from the web service response
        pH_values = response_pH.timeSeries[0].values[0].value
        Temp_values = response_Temp.timeSeries[0].values[0].value
        DO_values = response_DO.timeSeries[0].values[0].value
        N_values = response_N.timeSeries[0].values[0].value


        # Loop through the values and load into the blank lists using append

        for v in pH_values:
            if float(v.value) > -100.0:
                a1.append(float(v.value))
                b1.append(v._dateTime)
        for v in Temp_values:
            if float(v.value) > -100.0:
                a2.append(float(v.value))
                b2.append(v._dateTime)
        for v in DO_values:
            if float(v.value) > -100.0:
                a3.append(float(v.value))
                b3.append(v._dateTime)
        for v in N_values:
            if float(v.value) > -100.0:
                a4.append(float(v.value))
                b4.append(v._dateTime)

        # Create a Pandas Series object from the lists
        # Set the index of the Series object to the dates
        pH_ts = Series(a1, index=b1)
        Temp_ts = Series(a2, index=b2)
        DO_ts = Series(a3, index=b3)
        N_ts = Series(a4, index=b4)
        print Temp_ts


        # fig, ax = plt.subplots()
        # pH_ts.plot(color='red', linestyle='-', label='15-minute pH values')
        # Temp_ts.plot(color='green', linestyle='-', label='15-minute Temperature values')
        # DO_ts.plot(color='blue', linestyle='-', label='15-minute DO values')
        # N_ts.plot(color='black', linestyle='-', label='15-minute Nitrate-N values')
        #
        # ax.set_ylabel('Values')
        # ax.set_xlabel('Date')
        # ax.grid(True)
        # ax.set_title("pH, Temperature, DO, Nitrate-N values at iUTAH site: "+siteName)
        # legend = ax.legend(loc='upper right', shadow=False)
        # plt.show()






    return JsonResponse({'success': "123",
                         'a1': a1,
                         'b1': b1,
                         'a2': a2,
                         'b2': b2,
                         'a3': a3,
                         'b3': b3,
                         'a4': a4,
                         'b4': b4
                         })