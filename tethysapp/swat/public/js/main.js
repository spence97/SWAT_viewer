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
        var projection = ol.proj.get('EPSG:4326');
        var baseLayer = new ol.layer.Tile({
            source: new ol.source.BingMaps({
                key: '5TC0yID7CYaqv3nVQLKe~xWVt4aXWMJq2Ed72cO4xsA~ApdeyQwHyH_btMjQS1NJ7OHKY8BK-W-EMQMrIavoQUMYXeZIQOUURnKGBOC7UCt4',
                imagerySet: 'Road' // Options 'Aerial', 'AerialWithLabels', 'Road'
            })
        });

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



        featureOverlayStream = new ol.layer.Vector({
            source: new ol.source.Vector()
        });

        featureOverlaySubbasin = new ol.layer.Vector({
            source: new ol.source.Vector()
        });

        var view = new ol.View({
            center: [104.5, 17.5],
            projection: projection,
            zoom: 6.8
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
        element = document.getElementById('popup');

        popup = new ol.Overlay({
            element: element,
            positioning: 'bottom-center',
            stopEvent: true
        });

        map.addOverlay(popup);


    };

    get_time_series = function(start, end, parameters, streamID) {
        console.log(parameters)

        $.ajax({
            type: 'POST',
            url: '/apps/swat/timeseries/',
            data: {
                'startDate': start,
                'endDate': end,
                'parameters': parameters,
                'streamID': streamID
            },
            error: function () {
                $('#info').html('<p class="alert alert-danger" style="text-align: center"><strong>An unknown error occurred while retrieving the forecast</strong></p>');
                $('#info').removeClass('hidden');

                setTimeout(function () {
                    $('#info').addClass('hidden')
                }, 5000);
            },
            success: function (data) {
                var values = data.Values
                console.log(values)
                var dates = data.Dates
                var parameters = data.Parameters
                console.log(parameters)
                var names = data.Names
                console.log(names)
                var reachId = data.ReachID


                if (!data.error) {
                    $loading.addClass('hidden');
                    $('#container').removeClass('hidden');
                    $('#download_data').removeClass('hidden');

                }
//                if (parameters.length == 1) {
//
//                    Highcharts.chart('container', {
//                        chart: {
//                            type: 'line',
//                            zoomType: 'x'
//                        },
//                        title: {
//                            text: names[0] + " at reach " + reachId
//                        },
//                        subtitle: {
//                            text: document.ontouchstart === undefined ?
//                                'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
//                        },
//                        xAxis: {
//                            type: 'datetime',
//                            startonTick: true
//                        },
//                        yAxis: {
//                            title: {
//                                text: names[0]
//                            },
//                            min: 0,
//                            minPadding: 0,
//                            startOnTick: true
//                        },
//                        legend: {
//                            enabled: true
//                        },
//                        plotOptions: {
//                            area: {
//                                fillColor: {
//                                    linearGradient: {
//                                        x1: 0,
//                                        y1: 0,
//                                        x2: 0,
//                                        y2: 1
//                                    },
//                                    stops: [
//                                        [0, '#197ccc'],
//                                        [1, Highcharts.Color('#197ccc').setOpacity(0).get('rgba')]
//                                    ]
//                                },
//                                marker: {
//                                    radius: 1
//                                },
//                                lineWidth: 1,
//                                states: {
//                                    hover: {
//                                        lineWidth: 1
//                                    }
//                                },
//                                threshold: null
//                            }
//                        },
//
//                        series: [{
//                            type: 'area',
//                            name: parameters[0],
//                            data: values[0]
//                        }]
//                    });
//                } else {
                    var seriesOptions = []
                    var seriesCounter = 0
                    var yAxes = []
                    var plot_height = 100/parameters.length - 2
                    var plot_height_str = plot_height + '%'
                    var top = []
                    var colors = ['#002cce','#c10000', '#0e6d00', '#7400ce']

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
                            endOnTick: false
                        }


                        seriesCounter += 1;

                        if (seriesCounter === names.length) {
                            Highcharts.stockChart('container', {

                                rangeSelector: {
                                    enabled: false
                                },

                                title: {
                                    text: 'SWAT Time-series Comparisons'
                                },

                                subtitle: {
                                    text: names.toString().split(',').join(', ')
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
                                    pointFormat: '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b>',
                                    valueDecimals: 2,
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
            var start = $('#start_pick').val();
            var end = $('#end_pick').val();
            var parameter = $('#param_select option:selected').val();
            map.removeLayer(featureOverlayStream);
            map.removeLayer(featureOverlaySubbasin);


            if (map.getTargetElement().style.cursor == "pointer") {
                if ((parameter === '') || (start === 'Select Start Date') || (end === 'Select End Date')) {
                    map.addLayer(featureOverlaySubbasin);
                    map.addLayer(featureOverlayStream);
                    window.alert("Please be sure to select a parameter, start date, and end date before selecting a stream.")
                } else {
                    $('#container').addClass('hidden')
                    $('#download_data').addClass('hidden');

                    $loading = $('#view-file-loading');
                    $loading.removeClass('hidden');
                    $("#ts-modal").modal('show');

                    var clickCoord = evt.coordinate;
                    popup.setPosition(clickCoord);
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
                               var streamID = parseFloat(result["features"][0]["properties"]["Subbasin"]);
                               var start = $('#start_pick').val();
                               var end = $('#end_pick').val();
                               $('#param_select option:selected').each(function() {
                                    parameters.push( $( this ).val());
                               });
                               console.log(parameters)

                               var streamVectorSource = new ol.source.Vector({
                                    format: new ol.format.GeoJSON(),
                                    url: 'http://localhost:8080/geoserver/wms/ows?service=wfs&version=2.0.0&request=getfeature&typename=swat_mekong:reach&CQL_FILTER=Subbasin='+streamID+'&outputFormat=application/json&srsname=EPSG:4326&,EPSG:4326',
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
                                    url: 'http://localhost:8080/geoserver/wms/ows?service=wfs&version=2.0.0&request=getfeature&typename=swat_mekong:subbasin&CQL_FILTER=Subbasin='+streamID+'&outputFormat=application/json&srsname=EPSG:4326&,EPSG:4326',
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
                               get_time_series(start, end, parameters, streamID);
    //
    //                           return(result);
                            },
                            error: function (XMLHttpRequest, textStatus, errorThrown) {
                                console.log(Error);
                            }
                        }).done(function(value) {
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

    add_streams = function(){
        var sld_string = '<StyledLayerDescriptor version="1.0.0"><NamedLayer><Name>swat_mekong:reach</Name><UserStyle><FeatureTypeStyle><Rule>\
            <Name>rule1</Name>\
            <Title>Blue Line</Title>\
            <Abstract>A solid blue line with a 2 pixel width</Abstract>\
            <LineSymbolizer>\
                <Stroke>\
                    <CssParameter name="stroke">#005fea</CssParameter>\
                    <CssParameter name="stroke-width">2</CssParameter>\
                </Stroke>\
            </LineSymbolizer>\
            </Rule>\
            </FeatureTypeStyle>\
            </UserStyle>\
            </NamedLayer>\
            </StyledLayerDescriptor>';



        wms_source = new ol.source.ImageWMS({
            url: 'http://localhost:8080/geoserver/wms',
            params: {'LAYERS':'swat_mekong:reach','SLD_BODY':sld_string},
            serverType: 'geoserver',
            crossOrigin: 'Anonymous'
        });

        streams_layer = new ol.layer.Image({
            source: wms_source
        });


        map.addLayer(streams_layer);

    };

    init_all = function(){
        init_map();
        init_events();
//        add_basins();
        add_streams();
    };

    function get_time_series(streadId, param, startDate, endDate) {

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


    });

    return public_interface;


}());// End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.