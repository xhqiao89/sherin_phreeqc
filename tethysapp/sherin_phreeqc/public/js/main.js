var map, sites_layer, click_point_layer;
var baseMapLayer=null;
var chart;


$(document).ready(function () {

    //Set basemap dropdownbox initial display as 'Bing'
    dropdown_obj=document.getElementById("select_basemap");
    dropdown_obj.selectedIndex=0;

    map = TETHYS_MAP_VIEW.getMap();

    //remove the default openstreetmap that Tethys adds.
    map.getLayers().clear();

    //build the bing map layer
	bing_layer = new ol.layer.Tile({

		source: new ol.source.BingMaps({
			imagerySet: 'AerialWithLabels',
			key: 'Ak-dzM4wZjSqTlzveKz5u0d4IQ4bRzVI309GxmkgSVr1ewS6iPSrOvOKhA-CJlm3'
		})
	});

    //build OpenStreet map layer
    openstreet_layer = new ol.layer.Tile({
          source: new ol.source.OSM()
        });

    sites_layer = new ol.layer.Vector({
	  		    source: new ol.source.Vector({
    			//projection: ol.proj.get('EPSG:4326'),
                format:new ol.format.KML(),
    			//normally this kml file would be sitting on your server
    			url: '/static/sherin_phreeqc/kml/Sites.kml'

  			})
		});

    click_point_layer = new ol.layer.Vector({
      source: new ol.source.Vector(),
      style: new ol.style.Style({
        fill: new ol.style.Fill({
          color: 'rgba(255, 255, 255, 0.2)'
        }),
        stroke: new ol.style.Stroke({
          color: '#ffcc33',
          width: 2
        }),
        image: new ol.style.Circle({
          radius: 7,
          fill: new ol.style.Fill({
            color: '#ffcc33'
          })
        })
      })
    });

    //set bing map as base map
    baseMapLayer=bing_layer;

    map.addLayer(baseMapLayer);
    map.addLayer(sites_layer);
    map.addLayer(click_point_layer);

    var lat = 41.30108;
    var lon = -111.29661;
    CenterMap(lat, lon);
    map.getView().setZoom(7);

    //map.on('click', function(evt) {
    //    var coordinate = evt.coordinate;
    //
    //    var lonlat = ol.proj.transform(coordinate, 'EPSG:3857', 'EPSG:4326');
    //
    //    //Each time the user clicks on the map, let's run the point
    //    //indexing service to show them the closest NHD reach segment.
    //    run_phreeqc_analyze(lonlat);
    //})

    var chart_options = {
	chart: {
		renderTo: 'iutah-chart',
		zoomType: 'x',
	},
        loading: {
            labelStyle: {
                top: '45%',
		        left: '50%',
                display: 'block',
                width: '134px',
                height: '100px',
                backgroundColor: '#000'
            }
        },
	title: {
		text: 'iUTAH GAMUT DATA'
	},
    xAxis: {
		type: 'datetime',
		//minRange: 14 * 24 * 3600000
		},
	yAxis: {
		title: {
			text: 'Value'
		},
		},
	legend: {
		enabled: true
	},
	series: [{},{},{},{},{}]
};

    chart_options.series[0].type = 'line';
    chart_options.series[0].name = 'pH';
    chart_options.series[1].type = 'line';
    chart_options.series[1].name = 'Temperature';
    chart_options.series[2].type = 'line';
    chart_options.series[2].name = 'DO';
    chart_options.series[3].type = 'line';
    chart_options.series[3].name = 'Nitrate-N';
    chart_options.series[4].type = 'line';
    chart_options.series[4].name = 'Daily average pH';

    chart = new Highcharts.Chart(chart_options);

});

function run_select_basemap() {

    dropdown_obj = document.getElementById("select_basemap");
    selected_index = dropdown_obj.selectedIndex;
    selected_value = dropdown_obj.options[selected_index].value;

    new_baseMapLayer = null;
    if (selected_value == "bing_layer") {
        new_baseMapLayer = bing_layer
    }
       else if (selected_value == "openstreet_layer") {
        new_baseMapLayer = openstreet_layer;
    }

        //remove base map layer
    //insert selected layer as basemap
    map.removeLayer(baseMapLayer);
    map.getLayers().insertAt(0, new_baseMapLayer);
    baseMapLayer=new_baseMapLayer
}

function CenterMap(lat, lon){
    var dbPoint = {
        "type": "Point",
        "coordinates": [lon, lat],
    }
    var coords = ol.proj.transform(dbPoint.coordinates, 'EPSG:4326','EPSG:3857');
    map.getView().setCenter(coords);
}

function run_select_site() {
    var site_dropdown = document.getElementById("select_site");
    var ID = site_dropdown.options[site_dropdown.selectedIndex].value;
    myFeature = sites_layer.getSource().getFeatures();

    var feature;
    for (i = 0; i < myFeature.length; i++) {
        feature = myFeature[i];
        if (feature.q.name == ID) {
            myCoords = feature.getGeometry().getCoordinates();
            map.getView().setCenter(myCoords);
            map.getView().setZoom(15);

        //    lizhiyu is xin ji boy
        }
    }

}


function ymdThms2Date(str){
    var ymd = str.split("T")[0];
    var hms = str.split("T")[1];
    var year = parseInt(ymd.split("-")[0]);
    var month = parseInt(ymd.split("-")[1])-1;
    var day = parseInt(ymd.split("-")[2]);
    var hour = parseInt(hms.split(":")[0]);
    var minute = parseInt(hms.split(":")[1]);
    var second = parseInt(hms.split(":")[2]);
    d = Date.UTC(year, month, day, hour, minute, second);
    return d
}

function createOneSeriesData(y_list, t_list){
    ty_list = []
    for (i=0; i<y_list.length; i++)
        {
         var y = y_list[i]
         var t = ymdThms2Date(t_list[i])
         ty = [t, y]
         ty_list.push(ty)
        }
    return ty_list
}


function average_values(elmt){
    var sum = 0;
    for( var i = 0; i < elmt.length; i++ ){
    sum += parseFloat(elmt[i]); //don't forget to add the base
}
    var avg = sum/(elmt.length*1.0);
    return avg;

}

var pH_ave;
var Temp_ave;
var DO_ave;
var N_ave;

function run_search_results(){
    var site_dropdown = document.getElementById("select_site");
    var siteCode = site_dropdown.options[site_dropdown.selectedIndex].value;
    var beginDate = document.getElementById("begin_date").value;
    var endDate = document.getElementById("end_date").value;
    waiting_pis();

     $.ajax({
         type: 'GET',
         url: 'search-gamut-data',
         dataType: 'json',
         data: {
             'siteCode': siteCode,
             'beginDate': beginDate,
             'endDate': endDate
         },
         success: function (data) {
             document.getElementById("result_loading").innerHTML = '';
             var a1 = data.a1;
             var b1 = data.b1;
             var a2 = data.a2;
             var b2 = data.b2;
             var a3 = data.a3;
             var b3 = data.b3;
             var a4 = data.a4;
             var b4 = data.b4;
             var a5 = data.a5;
             var b5 = data.b5;

             chart.series[0].setData(createOneSeriesData(a1, b1));
             chart.series[1].setData(createOneSeriesData(a2, b2));
             chart.series[2].setData(createOneSeriesData(a3, b3));
             chart.series[3].setData(createOneSeriesData(a4, b4));
             chart.series[4].setData(createOneSeriesData(a5, b5));

             pH_ave = average_values(a1);
             Temp_ave = average_values(a2);
             DO_ave = average_values(a3);
             N_ave = average_values(a4);

         },

         error: function (jqXHR, textStatus, errorThrown) {
             alert("Error");
         }
     });
    }

function run_phreeqc_analyze(lonlat) {
    var input_data = document.getElementById("xValue").value;
        $.ajax({
         type: 'GET',
         url: 'run-phreeqc',
         dataType: 'json',
         data: {
             'temp': Temp_ave,
             'pH': pH_ave,
             'DO': DO_ave,
             'N': N_ave,
             'Ca': input_data
         },
         success: function (data) {

             alert("Finished!")

             var m_H = data["m_H"].toPrecision(4);
             var m_OH= data["m_OH"].toPrecision(4);
             var m_Ca = data["m_Ca"].toExponential(3);
             var m_CaOH = data["m_CaOH"].toPrecision(4);
             var m_Ca2 = data["m_Ca2"].toExponential(3);

             $('#m_H').val(m_H);
             $('#m_OH').val(m_OH);
             $('#m_Ca').val(m_Ca);
             $('#m_CaOH').val(m_CaOH);
             $('#m_Ca2').val(m_Ca2);

                      },

         error: function (jqXHR, textStatus, errorThrown) {
             alert("Error");
         }
     });

}

function waiting_pis() {
     var wait_text = "<strong>Loading...</strong><br>" +
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src='/static/sherin_phreeqc/images/earth_globe.gif'>";
    document.getElementById('result_loading').innerHTML = wait_text;
}
