var map, sites_layer, click_point_layer;
var flag_geocoded;

var baseMapLayer=null;


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
    			url: '/static/sherin_phreeqc/kml/iUTAH_sites.kml'

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
    map.getView().setZoom(8);

    map.on('click', function(evt) {
        flag_geocoded=false;
        var coordinate = evt.coordinate;
        addClickPoint(coordinate);

        var lonlat = ol.proj.transform(coordinate, 'EPSG:3857', 'EPSG:4326');

        //Each time the user clicks on the map, let's run the point
        //indexing service to show them the closest NHD reach segment.
        run_phreeqc_analyze(lonlat);
    })

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

function addClickPoint(coordinates){
    // Check if the feature exists. If not then create it.
    // If it does exist, then just change its geometry to the new coords.
    var geometry = new ol.geom.Point(coordinates);
    if (click_point_layer.getSource().getFeatures().length==0){
        var feature = new ol.Feature({
            geometry: geometry,
            attr: 'Some Property'
        });
        click_point_layer.getSource().addFeature(feature);
    } else {
        click_point_layer.getSource().getFeatures()[0].setGeometry(geometry);
    }
}

function CenterMap(lat, lon){
    var dbPoint = {
        "type": "Point",
        "coordinates": [lon, lat],
    }
    var coords = ol.proj.transform(dbPoint.coordinates, 'EPSG:4326','EPSG:3857');
    map.getView().setCenter(coords);
}

function run_select_site(){
  dropdown_obj = document.getElementById("select_site");

}

function run_phreeqc_analyze(lonlat) {

}
