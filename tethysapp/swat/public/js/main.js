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
        map,
        popup,
        $plotModal,
        public_interface,			// Object returned by the module
        variable_data,
        wms_workspace,
        geoserver_url = 'http://216.218.240.206:8181/geoserver/wms/',
        wms_url,
        wms_layer,
        basin_layer,
        streams_layer,
        featureOverlayStream,
        featureOverlaySubbasin,
        $loading,
        wms_source;

    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
    var add_basins,
        add_streams,
        init_events,
        init_all,
        get_time_series,
        update_dates,
        init_map,
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

    get_time_series = function(watershed, start, end, parameters, streamID) {
//      Function to pass selected dates, parameters, and streamID to the rch data parser python function and then plot the data
        var monthOrDay
        if ($(".toggle").hasClass( "off" )) {
            monthOrDay = 'Daily'
        } else {
            monthOrDay = 'Monthly'
        }
        console.log(watershed, start, end, parameters, streamID, monthOrDay)
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
//
            var start = $('#start_pick').val();
            console.log(start)
            var end = $('#end_pick').val();
            console.log(end)
            var parameter = $('#param_select option:selected').val();
            map.removeLayer(featureOverlayStream);
            map.removeLayer(featureOverlaySubbasin);


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
                    $("#ts-modal").modal('show');

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
                                console.log(result)
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
                               var start = $('#start_pick').val();
                               var end = $('#end_pick').val();
                               $('#param_select option:selected').each(function() {
                                    parameters.push( $( this ).val());
                               });

                               var streamVectorSource = new ol.source.Vector({
                                    format: new ol.format.GeoJSON(),
                                    url: geoserver_url + 'ows?service=wfs&version=2.0.0&request=getfeature&typename='+reach_store_id+'&CQL_FILTER=Subbasin='+streamID+'&outputFormat=application/json&srsname=EPSG:4326&,EPSG:4326',
                                    strategy: ol.loadingstrategy.bbox
                               });

                               featureOverlayStream = new ol.layer.Vector({
                                    source: streamVectorSource,
                                    style: new ol.style.Style({
                                        stroke: new ol.style.Stroke({
                                            color: '#1500ff',
                                            width: 4
                                        })
                                    })
                               });

                               var subbasinVectorSource = new ol.source.Vector({
                                    format: new ol.format.GeoJSON(),
                                    url: geoserver_url + 'ows?service=wfs&version=2.0.0&request=getfeature&typename='+basin_store_id+'&CQL_FILTER=Subbasin='+streamID+'&outputFormat=application/json&srsname=EPSG:4326&,EPSG:4326',
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

                               map.addLayer(featureOverlaySubbasin);
                               map.addLayer(featureOverlayStream);
                               get_time_series(watershed, start, end, parameters, streamID);
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
                    var layers = xml.getElementsByTagName("Layer");
                    var parser = new ol.format.WMSCapabilities();
                    var result = parser.read(xml);
                    var layers = result['Capability']['Layer']['Layer']
                    for (var i=0; i<layers.length; i++) {
                        if(layers[i].Title == store + '-basin') {
                            layer_xml = xml.getElementsByTagName('Layer')[i+1]
                            layerParams = layers[i]
                        }
                    }

                    srs = layer_xml.getElementsByTagName('SRS')[0].innerHTML
                    bbox = layerParams.BoundingBox[0].extent
                    console.log(srs, bbox)
                    var new_extent = ol.proj.transformExtent(bbox, srs, 'EPSG:4326');
                    var center = ol.extent.getCenter(new_extent)
                    console.log(center)
                    var view = new ol.View({
                        center: center,
                        projection: 'EPSG:4326',
                        extent: new_extent,
                        zoom: 6
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
                    <CssParameter name="stroke">#418ff4</CssParameter>\
                    <CssParameter name="stroke-width">2</CssParameter>\
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
              <CssParameter name="fill">#a9c5ce</CssParameter>\
              <CssParameter name="fill-opacity">.5</CssParameter>\
            </Fill>\
            <Stroke>\
              <CssParameter name="stroke">#2d2c2c</CssParameter>\
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

    init_all = function(){
        init_map();
        init_events();
        add_basins();
        add_streams();
    };


//  When the Monthly/Daily toggle is clicked, update the datepickers to show only available options
    update_dates = function() {
        if($(".toggle").hasClass( "off")) {
            var options = {
                format: 'MM d, yyyy',
                startDate: 'January 1, 2001',
                endDate: 'December 31, 2015',
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
            var options = {
                format: 'MM yyyy',
                startDate: 'January 2005',
                endDate: 'December 2015',
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
        $(".monthDayToggle").change(function(){
            update_dates();
            map.removeLayer(featureOverlaySubbasin);
            map.removeLayer(featureOverlayStream);
        });
        $("#upload").click(function() {
            $("#upload-modal").modal('show');
        });
        $("#watershed_select").change(function(){
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
    });




    return public_interface;


}());// End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.


// Old code to reference


//        var baseLayer = new ol.layer.Tile({
//            source: new ol.source.Stamen({
//                layer: 'terrain-background'
//            }),
//        })

//        var baseLayer = new ol.layer.Tile({
//            source: new ol.source.TileJSON({
//                url: 'https://api.tiles.mapbox.com/v3/mapbox.natural-earth-hypso-bathy.json?secure',
//                crossOrigin: 'anonymous'
//            }),
//        })

//    add_basins = function(){
//        var sld_string = '<StyledLayerDescriptor version="1.0.0"><NamedLayer><Name>swat_mekong:subbasin</Name><UserStyle><FeatureTypeStyle><Rule>\
//            <PolygonSymbolizer>\
//            <Name>rule1</Name>\
//            <Title>Watersheds</Title>\
//            <Abstract></Abstract>\
//            <Fill>\
//              <CssParameter name="fill">#a9c5ce</CssParameter>\
//              <CssParameter name="fill-opacity">0</CssParameter>\
//            </Fill>\
//            <Stroke>\
//              <CssParameter name="stroke">#2d2c2c</CssParameter>\
//              <CssParameter name="stroke-width">.5</CssParameter>\
//            </Stroke>\
//            </PolygonSymbolizer>\
//            </Rule>\
//            </FeatureTypeStyle>\
//            </UserStyle>\
//            </NamedLayer>\
//            </StyledLayerDescriptor>';
//
//        wms_source = new ol.source.ImageWMS({
//            url: 'http://localhost:8080/geoserver/wms',
//            params: {'LAYERS':'swat_mekong:subbasin','SLD_BODY':sld_string},
//            serverType: 'geoserver',
//            crossOrigin: 'Anonymous'
//        });
//
//        basin_layer = new ol.layer.Image({
//            source: wms_source
//        });
//
//
//        map.addLayer(basin_layer);
//
//    }


//    update_dates = function(){
//        if ($(".toggle").hasClass( "off" )) {
//            $("#datePickStart").load(' #start_pick');
//            $("#datePickEnd").load(' #end_pick');
//            $.ajax({
//                type: 'GET',
//                url: '/apps/swat/home/',
//                data: {
//                    'startDate': 'January 01, 2011',
//                    'endDate': 'January 02, 2011',
//                    'format': 'MM d, yyyy',
//                    'startView': 'year',
//                    'minView': 'days'
//                },
//            }).done(function() {
//
////                $(".form-control").attr("data-date-start-date", "January 01, 2011")
////                $(".form-control").attr("data-date-end-date", "January 02, 2011")
////                $(".form-control").attr("data-date-format", "MM d, yyyy")
////                $(".form-control").attr("data-date-start-view", "year")
////                $(".form-control").attr("data-date-min-view-mode", "days")
//            })
//        } else {
////            $("#datePickStart").load(' #start_pick');
////            $("#datePickEnd").load(' #end_pick');
////            $.ajax({
////                type: 'GET',
////                url: '/apps/swat/home/',
////                data: {
////                    'startDate': 'January 2005',
////                    'endDate': 'December 2015',
////                    'format': 'MM yyyy',
////                    'startView': 'decade',
////                    'minView': 'months'
////                },
////            }).done(function(){
//
////                $(".form-control").attr("data-date-start-date", "January 2005")
////                $(".form-control").attr("data-date-end-date", "December 2015")
////                $(".form-control").attr("data-date-format", "MM yyyy")
////                $(".form-control").attr("data-date-start-view", "decade")
////                $(".form-control").attr("data-date-min-view-mode", "months")
//            })
//        }
//    }


    //                        var streamID = parseFloat(value["features"][0]["properties"]["Subbasin"]);
    //                        console.log(streamID);
    //                        var parameter = $('#param_select option:selected').val();
    //                        console.log(parameter);
    //                        var start = $('#start_pick').val();
    //                        console.log(start);
    //                        var end = $('#end_pick').val();
    //                        console.log(end);

    //                        var popup_content = '<div class="stream-popup">' +
    //                                      '<p><b>' + 'Stream ID: ' + streamID + '</b></p>' +
    //                                      '<table class="table  table-condensed">' +
    //                                      '</table>' +
    //                                      '<div class="btn btn-success" data-toggle="tooltip" data-placement="bottom" title="View Plot">' +
    //                                        '<a data-toggle="modal" data-target="#plot-modal"> View Time-Series </a>' +
    //                                      '</div>' +
    ////                                      '<a class="btn btn-success" data-target="#plot-modal">View Time-Series</a>' +
    //                                      '</div>';
    //
    //                        // Clean up last popup and reinitialize
    //                        $(element).popover('destroy');
    //
    //                        // Delay arbitrarily to wait for previous popover to
    //                        // be deleted before showing new popover.
    //                        setTimeout(function() {
    //                            popup.setPosition(clickCoord);
    //
    //                            $(element).popover({
    //                                'placement': 'top',
    //                                'animation': true,
    //                                'html': true,
    //                                'content': popup_content
    //                            });
    //
    //                              $(element).popover('show');
    //                          }, 500);
