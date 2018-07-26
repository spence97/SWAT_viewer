/*****************************************************************************
 * FILE:    SWAT Viewer MAIN JS
 * DATE:    3/28/18
 * AUTHOR: Spencer McDonald
 * COPYRIGHT:
 * LICENSE:
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var LIBRARY_OBJECT = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
        var current_layer,
        element,
        layers,
        modal_map,
        map,
        popup,
        $plotModal,
        public_interface,			// Object returned by the module
        variable_data,
        wms_workspace,
        geoserver_url = 'http://216.218.240.206:8080/geoserver/wms/',
//        geoserver_url = 'http://localhost:8080/geoserver/wms',
        cql_filter,
        upstreams,
        wms_url,
        wms_layer,
        basin_layer,
        streams_layer,
        lulc_layer,
        soil_layer,
        featureOverlayStream,
        featureOverlaySubbasin,
        $loading,
        wms_source;

    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
    var add_basins,
        add_lulc,
        add_soil,
        add_streams,
        init_events,
        init_all,
        get_time_series,
        update_selectors,
        toggleLayers,
        init_map,
        init_modal_map,
        downloadCsv,
        downloadAscii,
        getCookie




    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/
//Get a CSRF cookie for request
getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//find if method is csrf safe
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

//add csrf token to appropriate ajax requests
$(function() {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            }
        }
    });
}); //document ready


//send data to database with error messages
function ajax_update_database(ajax_url, ajax_data) {
    //backslash at end of url is required
    if (ajax_url.substr(-1) !== "/") {
        ajax_url = ajax_url.concat("/");
    }
    //update database
    var xhr = jQuery.ajax({
        type: "POST",
        url: ajax_url,
        dataType: "json",
        data: ajax_data
    });
    xhr.done(function(data) {
        if("success" in data) {
            // console.log("success");
        } else {
            console.log(xhr.responseText);
        }
    })
    .fail(function(xhr, status, error) {
        console.log(xhr.responseText);
    });

    return xhr;
}

    init_map = function() {
//      Initialize all the initial map elements (projection, basemap, layers, center, zoom)
        var projection = ol.proj.get('EPSG:4326');
        var baseLayer = new ol.layer.Tile({
            source: new ol.source.BingMaps({
                key: '5TC0yID7CYaqv3nVQLKe~xWVt4aXWMJq2Ed72cO4xsA~ApdeyQwHyH_btMjQS1NJ7OHKY8BK-W-EMQMrIavoQUMYXeZIQOUURnKGBOC7UCt4',
                imagerySet: 'AerialWithLabels' // Options 'Aerial', 'AerialWithLabels', 'Road'
            })
        });

        featureOverlayStream = new ol.layer.Vector({
            source: new ol.source.Vector()
        });

        featureOverlaySubbasin = new ol.layer.Vector({
            source: new ol.source.Vector()
        });

        var view = new ol.View({
            center: [104.5, 17.5],
            projection: projection,
            zoom: 5.5
        });
        wms_source = new ol.source.ImageWMS();

        wms_layer = new ol.layer.Image({
            source: wms_source
        });

        layers = [baseLayer, featureOverlayStream, featureOverlaySubbasin];

        map = new ol.Map({
            target: document.getElementById("map"),
            layers: layers,
            view: view
        });

        map.crossOrigin = 'anonymous';


    };

    init_modal_map = function() {
//      Initialize all the initial map elements (projection, basemap, layers, center, zoom)
        var projection = ol.proj.get('EPSG:4326');
        var baseLayer = new ol.layer.Tile({
            source: new ol.source.BingMaps({
                key: '5TC0yID7CYaqv3nVQLKe~xWVt4aXWMJq2Ed72cO4xsA~ApdeyQwHyH_btMjQS1NJ7OHKY8BK-W-EMQMrIavoQUMYXeZIQOUURnKGBOC7UCt4',
                imagerySet: 'AerialWithLabels' // Options 'Aerial', 'AerialWithLabels', 'Road'
            })
        });

        featureOverlayStream = new ol.layer.Vector({
            source: new ol.source.Vector()
        });

        featureOverlaySubbasin = new ol.layer.Vector({
            source: new ol.source.Vector()
        });

        var view = new ol.View({
            center: [104.5, 17.5],
            projection: projection,
            zoom: 5.5
        });

        wms_source = new ol.source.ImageWMS();

        wms_layer = new ol.layer.Image({
            source: wms_source
        });

        layers = [baseLayer, featureOverlayStream, featureOverlaySubbasin];

        modal_map = new ol.Map({
            target: document.getElementById("modal_map"),
            layers: layers,
            view: view
        });

        map.crossOrigin = 'anonymous';

    };


    get_time_series = function(watershed, start, end, parameters, streamID) {
//      Function to pass selected dates, parameters, and streamID to the rch data parser python function and then plot the data
        var monthOrDay
        if ($(".toggle").hasClass( "off" )) {
            monthOrDay = 'Daily'
        } else {
            monthOrDay = 'Monthly'
        }
//      AJAX call to the timeseries python controller to run the rch data parser function
        $.ajax({
            type: 'POST',
            url: '/apps/swat/timeseries/',
            data: {
                'watershed': watershed,
                'startDate': start,
                'endDate': end,
                'parameters': parameters,
                'streamID': streamID,
                'monthOrDay': monthOrDay
            },
            error: function () {
                $('#error').html('<p class="alert alert-danger" style="text-align: center"><strong>An unknown error occurred while retrieving the data. Please try again</strong></p>');
                $('#error').removeClass('hidden');
                $loading.addClass('hidden')

                setTimeout(function () {
                    $('#error').addClass('hidden')
                }, 20000);
            },
            success: function (data) {
//              Take the resulting json object from the python function and plot it using the Highcharts API
                var values = data.Values
                var dates = data.Dates
                var parameters = data.Parameters
                var names = data.Names
                var reachId = data.ReachID


                if (!data.error) {
                    $loading.addClass('hidden');
                    $('#container').removeClass('hidden');
                    $('#download_csv').removeClass('hidden');
                    $('#download_ascii').removeClass('hidden');

                }
                    var plot_title
                    var plot_subtitle
                    if (parameters.length == 1) {
                        plot_title = 'SWAT Output Data'
                        plot_subtitle = 'ReachID: ' + reachId + ', Parameter: ' + names[0]
                    } else {
                        plot_title = 'SWAT Output Data Comparisons'
                        plot_subtitle = 'ReachID: ' + reachId + ', Parameters: ' + names.toString().split(',').join(', ')
                    }

                    var seriesOptions = []
                    var seriesCounter = 0
                    var plot_height = 100/parameters.length - 2
                    var plot_height_str = plot_height + '%'
                    var top = []
                    var yAxes = []
                    var colors = ['#002cce','#c10000', '#0e6d00', '#7400ce']
                    var data_tag
                    if (monthOrDay == 'Monthly') {
                       data_tag = '{point.y:,.1f}'
                    } else {
                       data_tag = '{point.y:,.1f}'
                    }

                    $.each( names, function( i, name ) {
                        seriesOptions[i] = {
                            type: 'area',
                            name: name,
                            data: values[i],
                            yAxis: i,
                            color: colors[i],
                            lineWidth: 1
                        };

                        var plot_top = plot_height * i + 2 * i
                        top.push(plot_top +'%')

                        yAxes[i] = {
                            labels: {
                                align: 'right',
                                x: -3
                            },
                            opposite: false,
                            min: 0,
                            title: {
                              text: name
                            },
                            offset: 0,
                            top: top[i],
                            height: plot_height_str,
                            lineWidth: 1,
                            endOnTick: false,
                            gridLineWidth: 0
                        }


                        seriesCounter += 1;

                        if (seriesCounter === names.length) {
                            Highcharts.setOptions({
                                lang: {
                                    thousandsSep: ','
                                }
                            });
                            Highcharts.stockChart('container', {

                                rangeSelector: {
                                    enabled: false
                                },

                                title: {
                                    text: plot_title
                                },

                                subtitle: {
                                    text: plot_subtitle
                                },

                                xAxis: {
                                    type: 'datetime',
                                    startonTick: true
                                },

                                yAxis: yAxes,


                                plotOptions: {
                                    series: {
                                        showInNavigator: true
                                    }
                                },

                                tooltip: {
                                    pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>' + data_tag + '</b>',
                                    valueDecimals: 2 ,
                                    split: true
                                },

                                series: seriesOptions
                            });
                        }
                    });
            }
        });
    };


    init_events = function(){
//      Initialize all map interactions
        var options = {
                format: 'MM yyyy',
                startDate: 'January 2005',
                endDate: 'December 2015',
                startView: 'decade',
                minViewMode: 'months',
                orientation: 'bottom auto'
            }
        $('.input-daterange input').each(function() {
            $(this).datepicker(options);
        });
        (function () {
            var target, observer, config;
            // select the target node
            target = $('#app-content-wrapper')[0];

            observer = new MutationObserver(function () {
                window.setTimeout(function () {
                    map.updateSize();
                }, 350);
            });
            $(window).on('resize', function () {
                map.updateSize();

            });


            config = {attributes: true};

            observer.observe(target, config);
        }());

        map.on("singleclick",function(evt){
            var clickCoord = evt.coordinate;
            var start = $('#start_pick').val();
            var end = $('#end_pick').val();
            var parameter = $('#param_select option:selected').val();
            map.removeLayer(featureOverlayStream);
            map.removeLayer(featureOverlaySubbasin);
            modal_map.removeLayer(featureOverlayStream);
            modal_map.removeLayer(featureOverlaySubbasin);


            if (map.getTargetElement().style.cursor == "pointer") {
                if ((parameter === undefined) || (start == 'Start Date') || (end == 'End Date')) {
                    map.addLayer(featureOverlaySubbasin);
                    map.addLayer(featureOverlayStream);
                    window.alert("Please be sure to select a parameter, start date, and end date before selecting a stream.")
                } else {
                    $('#container').addClass('hidden')
                    $('#download_csv').addClass('hidden');
                    $('#download_ascii').addClass('hidden');

                    $loading = $('#view-file-loading');
                    $loading.removeClass('hidden');
                    if (!$('#error').hasClass('hidden')) {
                        $('#error').addClass('hidden')
                    }



                    var store = $('#watershed_select option:selected').val()
                    var reach_store_id = 'swat:' + store + '-reach'
                    var basin_store_id = 'swat:' + store + '-subbasin'


                    var clickCoord = evt.coordinate;
                    var view = map.getView();
                    var viewResolution = view.getResolution();

                    var wms_url = current_layer.getSource().getGetFeatureInfoUrl(evt.coordinate, viewResolution, view.getProjection(), {'INFO_FORMAT': 'application/json'}); //Get the wms url for the clicked point
                    if (wms_url) {
                        //Retrieving the details for clicked point via the url
                        $.ajax({
                            type: "GET",
                            url: wms_url,
                            dataType: 'json',
                            success: function (result) {
                                var parameters = [];
                                if (parseFloat(result["features"].length < 1)) {
                                    $('#error').html('<p class="alert alert-danger" style="text-align: center"><strong>An unknown error occurred while retrieving the data. Please try again</strong></p>');
                                    $('#error').removeClass('hidden');
                                    $loading.addClass('hidden')

                                    setTimeout(function () {
                                        $('#error').addClass('hidden')
                                    }, 5000);
                                }
                                var streamID = parseFloat(result["features"][0]["properties"]["Subbasin"]);
                                var watershed = $('#watershed_select').val();


                                $.ajax({
                                    type: "POST",
                                    url: '/apps/swat/get_upstream/',
                                    data: {
                                        'watershed': watershed,
                                        'streamID': streamID
                                    },
                                    success: function(data) {

                                        upstreams = data.upstreams

                                        if (upstreams.length > 376) {
                                            cql_filter = 'Subbasin=' + streamID.toString();
                                        } else {
                                            cql_filter = 'Subbasin=' + streamID.toString();
                                            for (var i=1; i<upstreams.length; i++) {
                                                cql_filter += ' OR Subbasin=' + upstreams[i].toString();
                                            }
                                        }
                                        var reach_url = geoserver_url + 'ows?service=wfs&version=2.0.0&request=getfeature&typename='+reach_store_id+'&CQL_FILTER=Subbasin='+streamID+'&outputFormat=application/json&srsname=EPSG:4326&,EPSG:4326'
                                        var streamVectorSource = new ol.source.Vector({
                                            format: new ol.format.GeoJSON(),
                                            url: reach_url,
                                            strategy: ol.loadingstrategy.bbox
                                        });

                                        featureOverlayStream = new ol.layer.Vector({
                                            source: streamVectorSource,
                                            style: new ol.style.Style({
                                                stroke: new ol.style.Stroke({
                                                    color: '#f44242',
                                                    width: 4
                                                })
                                            })
                                        });

                                        var basin_url = geoserver_url + 'ows?service=wfs&version=2.0.0&request=getfeature&typename='+basin_store_id+'&CQL_FILTER='+cql_filter+'&outputFormat=application/json&srsname=EPSG:4326&,EPSG:4326'

                                        var subbasinVectorSource = new ol.source.Vector({
                                            format: new ol.format.GeoJSON(),
                                            url: basin_url,
                                            strategy: ol.loadingstrategy.bbox
                                        });

                                        var color = '#0dd8c0';
                                        color = ol.color.asArray(color);
                                        color = color.slice();
                                        color[3] = 0.5;

                                        featureOverlaySubbasin = new ol.layer.Vector({
                                            source: subbasinVectorSource,
                                            style: new ol.style.Style({
                                                stroke: new ol.style.Stroke({
                                                    color: '#000000',
                                                    width: 2
                                                }),
                                                fill: new ol.style.Fill({
                                                    color: color
                                                })
                                            })
                                        });
                                        var view = new ol.View({
                                            center: clickCoord,
                                            projection: 'EPSG:4326',
                                            zoom: 8.4
                                        });

                                        modal_map.setView(view)
                                        map.addLayer(featureOverlaySubbasin);
                                        map.addLayer(featureOverlayStream);
                                        modal_map.addLayer(featureOverlaySubbasin);
                                        modal_map.addLayer(featureOverlayStream);
                                        modal_map.updateSize();

                                        $.getJSON(basin_url, function(data) {
                                            console.log(data);
                                            var upstreamJson = data;
                                            $.ajax({
                                                type: 'POST',
                                                url: "/apps/swat/raster_compute/",
                                                data: JSON.stringify(upstreamJson),
                                                success: function(result){
                                                    console.log(result.hello)
                                                }
                                            })
                                        });
                                    }
                               })

                               var start = $('#start_pick').val();
                               var end = $('#end_pick').val();
                               $('#param_select option:selected').each(function() {
                                    parameters.push( $( this ).val());
                               });

                               get_time_series(watershed, start, end, parameters, streamID);
                               $("#ts-modal").modal('show');
                            },
                            error: function (XMLHttpRequest, textStatus, errorThrown) {

                                $('#error').html('<p class="alert alert-danger" style="text-align: center"><strong>An unknown error occurred while retrieving the data. Please try again</strong></p>');
                                $('#error').removeClass('hidden');
                                $loading.addClass('hidden')

                                setTimeout(function () {
                                    $('#error').addClass('hidden')
                                }, 5000);
                            }
                        }).done(function(value) {

                        });
                    }
                }
            }
        });

        map.on('pointermove', function(evt) {
            if (evt.dragging) {
                return;
            }
            var pixel = map.getEventPixel(evt.originalEvent);
            var hit = map.forEachLayerAtPixel(pixel, function(layer) {
                if (layer != layers[0]&& layer != layers[1]){
                    current_layer = layer;
                    return true;}
            });
            map.getTargetElement().style.cursor = hit ? 'pointer' : '';
        });

    };


    add_streams = function(){
//      add the streams for the selected watershed
        var store = $('#watershed_select option:selected').val()
        var store_id = 'swat:' + store + '-reach'
        if (store === 'lower_mekong') {
            var view = new ol.View({
                center: [104.5, 17.5],
                projection: 'EPSG:4326',
                zoom: 6.5
            });

            map.setView(view)

        } else {
            var layerParams
            var layer_xml
            var bbox
            var srs
            var wmsCapUrl = geoserver_url + '?service=WMS&version=1.1.1&request=GetCapabilities&'
//          Get the extent and projection of the selected watershed and set the map view to fit it
            $.ajax({
                type: "GET",
                url: wmsCapUrl,
                dataType: 'xml',
                success: function (xml) {
//                    var layers = xml.getElementsByTagName("Layer");
                    var parser = new ol.format.WMSCapabilities();
                    var result = parser.read(xml);
                    var layers = result['Capability']['Layer']['Layer']
                    for (var i=0; i<layers.length; i++) {
                        if(layers[i].Title == store + '-subbasin') {
                            layer_xml = xml.getElementsByTagName('Layer')[i+1]
                            layerParams = layers[i]
                        }
                    }

                    srs = layer_xml.getElementsByTagName('SRS')[0].innerHTML
                    bbox = layerParams.BoundingBox[0].extent
                    var new_extent = ol.proj.transformExtent(bbox, srs, 'EPSG:4326');
                    var center = ol.extent.getCenter(new_extent)
                    var view = new ol.View({
                        center: center,
                        projection: 'EPSG:4326',
                        extent: new_extent,
                        zoom: 8
                    });

                    map.setView(view)
                    map.getView().fit(new_extent, map.getSize());
                }
            });
        }

//      Set the style for the streams layer
        var sld_string = '<StyledLayerDescriptor version="1.0.0"><NamedLayer><Name>'+ store_id + '</Name><UserStyle><FeatureTypeStyle><Rule>\
            <Name>rule1</Name>\
            <Title>Blue Line</Title>\
            <Abstract>A solid blue line with a 2 pixel width</Abstract>\
            <LineSymbolizer>\
                <Stroke>\
                    <CssParameter name="stroke">#1500ff</CssParameter>\
                    <CssParameter name="stroke-width">1.2</CssParameter>\
                </Stroke>\
            </LineSymbolizer>\
            </Rule>\
            </FeatureTypeStyle>\
            </UserStyle>\
            </NamedLayer>\
            </StyledLayerDescriptor>';
//      Set the wms source to the url, workspace, and store for the streams of the selected watershed
        wms_source = new ol.source.ImageWMS({
            url: geoserver_url,
            params: {'LAYERS':store_id,'SLD_BODY':sld_string},
            serverType: 'geoserver',
            crossOrigin: 'Anonymous'
        });

        streams_layer = new ol.layer.Image({
            source: wms_source
        });

//      add streams to the map
        map.addLayer(streams_layer);

    };

    add_basins = function(){
//      add the streams for the selected watershed
        var store = $('#watershed_select option:selected').val()
        var store_id = 'swat:' + store + '-subbasin'
//      Set the style for the subbasins layer
        var sld_string = '<StyledLayerDescriptor version="1.0.0"><NamedLayer><Name>'+ store_id + '</Name><UserStyle><FeatureTypeStyle><Rule>\
            <PolygonSymbolizer>\
            <Name>rule1</Name>\
            <Title>Watersheds</Title>\
            <Abstract></Abstract>\
            <Fill>\
              <CssParameter name="fill">#adadad</CssParameter>\
              <CssParameter name="fill-opacity">.1</CssParameter>\
            </Fill>\
            <Stroke>\
              <CssParameter name="stroke">#ffffff</CssParameter>\
              <CssParameter name="stroke-width">.5</CssParameter>\
            </Stroke>\
            </PolygonSymbolizer>\
            </Rule>\
            </FeatureTypeStyle>\
            </UserStyle>\
            </NamedLayer>\
            </StyledLayerDescriptor>';

//      Set the wms source to the url, workspace, and store for the subbasins of the selected watershed
        wms_source = new ol.source.ImageWMS({
            url: geoserver_url,
            params: {'LAYERS':store_id,'SLD_BODY':sld_string},
            serverType: 'geoserver',
            crossOrigin: 'Anonymous'
        });

        basin_layer = new ol.layer.Image({
            source: wms_source
        });

//      add subbasins to the map
        map.addLayer(basin_layer);

    }

    add_lulc = function(){
//      add the streams for the selected watershed
        var store = 'lmrb_2010_lulc_map1'
        var store_id = 'swat:' + store

        var sld_string = '<StyledLayerDescriptor version="1.0.0"><NamedLayer><Name>'+store_id+'</Name><UserStyle><FeatureTypeStyle><Rule>\
            <RasterSymbolizer> \
            <ColorMap> \
            <ColorMapEntry color="#0055ff" quantity="10" label="water" opacity="1" />\
                <ColorMapEntry color="#91522f" quantity="15" label="barren - rock outcrops" opacity="0.7" />\
                <ColorMapEntry color="#ff0000" quantity="16" label="urban" opacity="0.7" />\
                <ColorMapEntry color="#ffadad" quantity="21" label="agriculture-rice-1 crop/year" opacity="0.7" />\
                <ColorMapEntry color="#ff54f0" quantity="22" label="agriculture-rice-2 crops/year" opacity="0.7" />\
                <ColorMapEntry color="#ffe100" quantity="23" label="agriculture-mixed annual crops-other than rice" opacity="0.7" />\
                <ColorMapEntry color="#ffae00" quantity="24" label="agriculture-shifting cultivation-cleared before 2010-herbaceous cover" opacity="0.7" />\
                <ColorMapEntry color="#912f08" quantity="25" label="agriculture-shifting cultivation-cleared in 2010" opacity="0.7" />\
                <ColorMapEntry color="#593200" quantity="26" label="agriculture-shifting cultivation-partially cleared in 2010" opacity="0.7" />\
                <ColorMapEntry color="#ed6600" quantity="31" label="deciduous shrubland-mixed scrub/herbaceous/low broadleaved forest" opacity="0.7" />\
                <ColorMapEntry color="#a0d89e" quantity="32" label="forest/scrub-deciduous broadleaved-low height" opacity="0.7" />\
                <ColorMapEntry color="#269924" quantity="33" label="forest-deciduous/evergreen-low/medium height" opacity="0.7" />\
                <ColorMapEntry color="#013d00" quantity="34" label="forest-evergreen broadleaved-medium/tall height" opacity="0.7" />\
                <ColorMapEntry color="#026801" quantity="35" label="forest-evergreen/deciduous broadleaved-low/medium height" opacity="0.7" />\
                <ColorMapEntry color="#99ff00" quantity="36" label="bamboo scrub/forest-low height-mostly evergreen" opacity="0.7" />\
                <ColorMapEntry color="#969696" quantity="41" label="grassland-sparse vegetation" opacity="0.7" />\
                <ColorMapEntry color="#8300db" quantity="42" label="industrial forest plantation-low/medium height" opacity="0.7" />\
                <ColorMapEntry color="#0092ed" quantity="43" label="wetland-mixed shrubland/herbaceous riparian areas" opacity="0.7" /></ColorMap>\
            </RasterSymbolizer>\
            </Rule>\
            </FeatureTypeStyle>\
            </UserStyle>\
            </NamedLayer>\
            </StyledLayerDescriptor>';


//      Set the wms source to the url, workspace, and store for the subbasins of the selected watershed
        wms_source = new ol.source.ImageWMS({
            url: geoserver_url,
            params: {'LAYERS':store_id,'SLD_BODY':sld_string},
            serverType: 'geoserver',
            crossOrigin: 'Anonymous'
        });

        lulc_layer = new ol.layer.Image({
            source: wms_source
        });

//      add subbasins to the map
        map.addLayer(lulc_layer);

    }

    add_soil = function(){
//      add the streams for the selected watershed
        var store = 'lmrb_soil_hwsd1'
        var store_id = 'swat:' + store

        var sld_string = '<StyledLayerDescriptor version="1.0.0"><NamedLayer><Name>'+store_id+'</Name><UserStyle><FeatureTypeStyle><Rule>\
            <RasterSymbolizer> \
            <ColorMap> \
            <ColorMapEntry color="#000000" quantity="65535" label="nodata" opacity="0.0" />\
                <ColorMapEntry color="#2471a3" quantity="4260" label="1" opacity="0.7" />\
                <ColorMapEntry color="#2e86c1" quantity="4261" label="1" opacity="0.7" />\
                <ColorMapEntry color="#3498db" quantity="4264" label="1" opacity="0.7" />\
                <ColorMapEntry color="#5dade2" quantity="4265" label="1" opacity="0.7" />\
                <ColorMapEntry color="#85c1e9" quantity="4267" label="1" opacity="0.7" />\
                <ColorMapEntry color="#a3e4d7" quantity="4284" label="1" opacity="0.7" />\
                <ColorMapEntry color="#d5f5e3" quantity="4325" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f9e79f" quantity="4383" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f4d03f" quantity="4393" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f5b041" quantity="4408" label="1" opacity="0.7" />\
                <ColorMapEntry color="#eb984e" quantity="4414" label="1" opacity="0.7" />\
                <ColorMapEntry color="#2471a3" quantity="4452" label="1" opacity="0.7" />\
                <ColorMapEntry color="#2e86c1" quantity="4464" label="1" opacity="0.7" />\
                <ColorMapEntry color="#3498db" quantity="4486" label="1" opacity="0.7" />\
                <ColorMapEntry color="#5dade2" quantity="4491" label="1" opacity="0.7" />\
                <ColorMapEntry color="#85c1e9" quantity="4494" label="1" opacity="0.7" />\
                <ColorMapEntry color="#a3e4d7" quantity="4499" label="1" opacity="0.7" />\
                <ColorMapEntry color="#d5f5e3" quantity="4502" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f9e79f" quantity="4544" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f4d03f" quantity="4587" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f5b041" quantity="4588" label="1" opacity="0.7" />\
                <ColorMapEntry color="#eb984e" quantity="6651" label="1" opacity="0.7" />\
                <ColorMapEntry color="#2471a3" quantity="11375" label="1" opacity="0.7" />\
                <ColorMapEntry color="#2e86c1" quantity="11604" label="1" opacity="0.7" />\
                <ColorMapEntry color="#3498db" quantity="11605" label="1" opacity="0.7" />\
                <ColorMapEntry color="#5dade2" quantity="11766" label="1" opacity="0.7" />\
                <ColorMapEntry color="#85c1e9" quantity="11770" label="1" opacity="0.7" />\
                <ColorMapEntry color="#a3e4d7" quantity="11772" label="1" opacity="0.7" />\
                <ColorMapEntry color="#d5f5e3" quantity="11782" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f9e79f" quantity="11783" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f4d03f" quantity="11786" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f5b041" quantity="11787" label="1" opacity="0.7" />\
                <ColorMapEntry color="#eb984e" quantity="11788" label="1" opacity="0.7" />\
                <ColorMapEntry color="#2471a3" quantity="11790" label="1" opacity="0.7" />\
                <ColorMapEntry color="#2e86c1" quantity="11794" label="1" opacity="0.7" />\
                <ColorMapEntry color="#3498db" quantity="11796" label="1" opacity="0.7" />\
                <ColorMapEntry color="#5dade2" quantity="11797" label="1" opacity="0.7" />\
                <ColorMapEntry color="#85c1e9" quantity="11798" label="1" opacity="0.7" />\
                <ColorMapEntry color="#a3e4d7" quantity="11800" label="1" opacity="0.7" />\
                <ColorMapEntry color="#d5f5e3" quantity="11804" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f9e79f" quantity="11805" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f4d03f" quantity="11808" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f5b041" quantity="11811" label="1" opacity="0.7" />\
                <ColorMapEntry color="#eb984e" quantity="11814" label="1" opacity="0.7" />\
                <ColorMapEntry color="#5dade2" quantity="11818" label="1" opacity="0.7" />\
                <ColorMapEntry color="#85c1e9" quantity="11821" label="1" opacity="0.7" />\
                <ColorMapEntry color="#a3e4d7" quantity="11839" label="1" opacity="0.7" />\
                <ColorMapEntry color="#d5f5e3" quantity="11840" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f9e79f" quantity="11843" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f4d03f" quantity="11844" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f5b041" quantity="11847" label="1" opacity="0.7" />\
                <ColorMapEntry color="#eb984e" quantity="11857" label="1" opacity="0.7" />\
                <ColorMapEntry color="#d5f5e3" quantity="11864" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f9e79f" quantity="11865" label="1" opacity="0.7" />\
                <ColorMapEntry color="#f4d03f" quantity="11868" label="1" opacity="0.7" />\
                <ColorMapEntry color="#e57e22" quantity="11869" label="1" opacity="0.7" /></ColorMap>\
            </RasterSymbolizer>\
            </Rule>\
            </FeatureTypeStyle>\
            </UserStyle>\
            </NamedLayer>\
            </StyledLayerDescriptor>';

//      Set the wms source to the url, workspace, and store for the subbasins of the selected watershed
        wms_source = new ol.source.ImageWMS({
            url: geoserver_url,
            params: {'LAYERS':store_id,'SLD_BODY':sld_string},
            serverType: 'geoserver',
            crossOrigin: 'Anonymous'
        });

        soil_layer = new ol.layer.Image({
            source: wms_source
        });

//      add subbasins to the map
        map.addLayer(soil_layer);

    }




//  When the Monthly/Daily toggle is clicked, update the datepickers to show only available options
    function loadXMLDoc() {
        var request = new XMLHttpRequest();
        request.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                update_selectors(this);
            }
        };
        request.open("GET", "/static/swat/watershed_data/watershed_info.xml", true);
        request.send();
    };


    update_selectors = function(xml) {
        var watershed, xmlDoc, x, i, watershed_num, start_date, end_date, params_list
        watershed = $('#watershed_select option:selected').val()
        xmlDoc = xml.responseXML;
        x = xmlDoc.getElementsByTagName('watershed');
        for (i = 0; i< x.length; i++) {
            var watershed_name = x[i].childNodes[0].innerHTML
            if (String(watershed_name) === String(watershed)) {
                watershed_num = i
            }
        }


        if ($(".toggle").hasClass( "off")) {
            start_date = xmlDoc.getElementsByTagName("day_start_date")[watershed_num].innerHTML
            end_date = xmlDoc.getElementsByTagName("day_end_date")[watershed_num].innerHTML
            var options = {
                format: 'MM d, yyyy',
                startDate: start_date,
                endDate: end_date,
                startView: 'decade',
                minViewMode: 'days',
                orientation: 'bottom auto'
            }
            $('.input-daterange input').each(function() {
                $(this).datepicker('setDate', null)
                $(this).datepicker('destroy');
                $(this).datepicker(options);
            });
        } else {
            start_date = xmlDoc.getElementsByTagName("month_start_date")[watershed_num].innerHTML;
            end_date = xmlDoc.getElementsByTagName("month_end_date")[watershed_num].innerHTML;
            var options = {
                format: 'MM yyyy',
                startDate: start_date,
                endDate: end_date,
                startView: 'decade',
                minViewMode: 'months',
                orientation: 'bottom auto'
            }
            $('.input-daterange input').each(function() {
                $(this).datepicker('setDate', null)
                $(this).datepicker('destroy');
                $(this).datepicker(options);
            });
        }
        $('#start_pick').attr('placeholder', 'Start Date')
        $('#end_pick').attr('placeholder', 'End Date')

    }

    toggleLayers = function() {
        if ($('#lulcOption').is(':checked')) {
            map.removeLayer(featureOverlaySubbasin)
            map.removeLayer(featureOverlayStream)
            map.removeLayer(soil_layer)
            map.removeLayer(basin_layer)
            map.removeLayer(streams_layer)
            add_lulc();
            add_basins();
            add_streams();
        } else if ($('#soilOption').is(':checked')) {
            map.removeLayer(featureOverlaySubbasin);
            map.removeLayer(featureOverlayStream);
            map.removeLayer(lulc_layer);
            map.removeLayer(basin_layer);
            map.removeLayer(streams_layer);
            add_soil();
            add_basins();
            add_streams();
        } else if ($('noneOption').is(':checked')) {
            map.removeLayer(featureOverlaySubbasin);
            map.removeLayer(featureOverlayStream);
            map.removeLayer(soil_layer);
            map.removeLayer(lulc_layer);
            map.removeLayer(basin_layer);
            map.removeLayer(streams_layer);
            add_basins();
            add_streams();
        }

    }

    init_all = function(){
        init_map();
        init_modal_map();
        init_events();
        add_basins();
        add_streams();
        loadXMLDoc();
    };


    /************************************************************************
     *                        DEFINE PUBLIC INTERFACE
     *************************************************************************/

    public_interface = {

    };

    /************************************************************************
     *                  INITIALIZATION / CONSTRUCTOR
     *************************************************************************/

    // Initialization: jQuery function that gets called when
    // the DOM tree finishes loading

$(function() {
        init_all();
        $("#start_pick").attr("autocomplete","off")
        $("#end_pick").attr("autocomplete","off")
        $("#id_watershed_name").attr("autocomplete","off")
        $(".monthDayToggle").change(function(){
            loadXMLDoc();
            map.removeLayer(featureOverlaySubbasin);
            map.removeLayer(featureOverlayStream);
        });
        $("#watershed_select").change(function(){
            loadXMLDoc();
            map.removeLayer(basin_layer);
            map.removeLayer(streams_layer);
            map.removeLayer(featureOverlaySubbasin);
            map.removeLayer(featureOverlayStream);
            add_basins();
            add_streams();
        });
        $(".form-group").change(function(){
            map.removeLayer(featureOverlaySubbasin);
            map.removeLayer(featureOverlayStream);
        })

        $(".radio").change(function(){
            toggleLayers();
        })

        $(".nav-tabs").click(function(){
            setTimeout(updatemap, 200);
            function updatemap() {
                if ($("#watershed_tab").hasClass('active')) {
                    modal_map.updateSize();
                }
            }
        })

})

    return public_interface;


}());// End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.

