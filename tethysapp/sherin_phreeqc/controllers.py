import os
import sys
import csv
from suds.client import Client
from pandas import Series
import logging
logging.getLogger('suds.client').setLevel(logging.CRITICAL)
sys.path.append('/usr/local/lib/python2.7/dist-packages')

from django.shortcuts import render
from django.http import JsonResponse
from tethys_gizmos.gizmo_options import MapView, MVView
from tethys_sdk.gizmos import Button, SelectInput, DatePicker, LinePlot, TextInput

MODE = 'dll'  # 'dll' or 'com'

if MODE == 'com':
    import phreeqpy.iphreeqc.phreeqc_com as phreeqc_mod
elif MODE == 'dll':
    import phreeqpy.iphreeqc.phreeqc_dll as phreeqc_mod
else:
    raise Exception('Mode "%s" is not defined use "com" or "dll".' % MODE)


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
    map_options = MapView(height='350px',
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
                            multiple=False,
                            options=[('Select a site', 'Select a site'), ('LR_Mendon_AA', 'LR_Mendon_AA'), ('LR_MainStreet_BA', 'LR_MainStreet_BA'),
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

    xValue = TextInput(display_text='Input Ca Concentration (ppm):',
                    name="xValue",
                    initial="",
                    disabled=False)

    btnPhreeqc = Button(display_text="Run Phreeqc",
                        name="btnPhreeqc",
                        attributes="id=btnPhreeqc onclick=run_phreeqc_analyze();",
                        submit=False)

    # Pass variables to the template via the context dictionary
    context = {'map_options': map_options,
               'select_basemap': select_basemap,
               'select_site': select_site,
               'btnSearch': btnSearch,
               'begin_date': begin_date,
               'end_date': end_date,
               'xValue': xValue,
               'btnPhreeqc':btnPhreeqc,
               }
    return render(request, 'sherin_phreeqc/home.html', context)


def search_gamut_data(request):

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

        # Create a new object named "NWIS" for calling the web service methods
        NWIS = Client(wsdlURL).service

        # Call the GetValuesObject method to return datavalues
        response_pH = NWIS.GetValuesObject(siteCode, variableCode_pH, beginDate, endDate,'')
        response_Temp = NWIS.GetValuesObject(siteCode, variableCode_Temp, beginDate, endDate, '')
        response_DO = NWIS.GetValuesObject(siteCode, variableCode_DO, beginDate, endDate, '')
        response_N = NWIS.GetValuesObject(siteCode, variableCode_N, beginDate, endDate, '')

        # Get the site's name from the response
        siteName = response_pH.timeSeries[0].sourceInfo.siteName

        # Create some blank lists in which to put the values and their dates
        a1 = []  # The pH values
        b1 = []  # The dates
        a2 = []  # The Temperature values
        b2 = []  # The dates
        a3 = []  # The DO values
        b3 = []  # The dates
        a4 = []  # The Nitrate-N values
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

        pH_ts = Series(a1, index=b1)
        dailyAvepH = pH_ts.resample('D', how='mean');
        dailyAvepH.to_csv("/tmp/avepH.csv")
        with open('/tmp/avepH.csv', 'rb') as f:
            reader = csv.reader(f)
            your_list = list(reader)
        a5=[]
        b5=[]
        for line in your_list:
            b5.append(line[0]+"T00:00:00")
            a5.append(float(line[1]))

    return JsonResponse({'success': "123",
                         'a1': a1,
                         'b1': b1,
                         'a2': a2,
                         'b2': b2,
                         'a3': a3,
                         'b3': b3,
                         'a4': a4,
                         'b4': b4,
                         'a5': a5,
                         'b5': b5,
                         })

def run_phreeqc(request):
    if request.method == 'GET':
        get_data = request.GET

        temp = str(get_data['temp'])
        pH = str(get_data['pH'])
        DO = str(get_data['DO'])
        N = str(get_data['N'])
        Ca = str(get_data['Ca'])

        rslt = phreeqc_func(temp, pH, DO, N, Ca)
        m_H2O = rslt["m_H2O(mol/kgw)"]
        m_CaOH = rslt["m_CaOH+(mol/kgw)"]
        m_Ca = rslt["Ca"]
        m_Ca2 = rslt["m_Ca+2(mol/kgw)"]
        m_H = rslt["m_H+(mol/kgw)"]
        m_OH = rslt["m_OH-(mol/kgw)"]

        return JsonResponse({'success': "123",
                            'm_H2O': m_H2O[0],
                             'm_CaOH': m_CaOH[0],
                             'm_Ca': m_Ca[0],
                             'm_Ca2': m_Ca2[0],
                             'm_H': m_H[0],
                             'm_OH': m_OH[0]})

def make_initial_conditions(temp,pH,DO,N,Ca):
    """
    Specify initial conditions data blocks.

    Uniform initial conditions are assumed.
    """
    initial_conditions = """
    SOLUTION 1
        units            ppm
        temp             %s
        pH               %s
        pe               7
        O(0)             %s
        N(5)             %s
        Ca               %s
    END
        """ % (temp, pH, DO, N, Ca)
    return initial_conditions

def make_selected_output(components):
    """
    Build SELECTED_OUTPUT data block
    """
    headings = "-headings  cb    H    O    "
    for i in range(len(components)):
        headings += components[i] + "\t"
    selected_output = """
    SELECTED_OUTPUT
        -reset false
        -molalities Ca+2 CaOH+ H+ OH- H2O
    USER_PUNCH
    """
    selected_output += headings + "\n"
    #
    # charge balance, H, and O
    #
    code = '10 w = TOT("water")\n'
    code += '20 PUNCH CHARGE_BALANCE, TOTMOLE("H"), TOTMOLE("O")\n'
    #
    # All other elements
    #
    lino = 30
    for component in components:
        code += '%d PUNCH w*TOT(\"%s\")\n' % (lino, component)
        lino += 10
    selected_output += code
    return selected_output

def get_selected_output(phreeqc):

    output = phreeqc.get_selected_output_array()
    header = output[0]
    conc = {}
    for head in header:
        conc[head] = []
    for row in output[1:]:
        for col, head in enumerate(header):
            conc[head].append(row[col])
    return conc

def phreeqc_func(temp, pH, DO, N, Ca):
    phreeqc = phreeqc_mod.IPhreeqc()
    module_dir = os.path.dirname(__file__)  # get current directory
    phreeqc.load_database(module_dir + "/phreeqc.dat")
    initial_conditions = make_initial_conditions(temp, pH, DO, N, Ca)
    phreeqc.run_string(initial_conditions)
    components = phreeqc.get_component_list();
    selected_output = make_selected_output(components)
    phreeqc.run_string(selected_output)
    phc_string = "RUN_CELLS; -cells 0-1\n"
    phreeqc.run_string(phc_string)
    output = phreeqc.get_selected_output_array()
    conc = get_selected_output(phreeqc)
    return conc

