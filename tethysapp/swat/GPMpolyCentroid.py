import rpy2.robjects as robjects

GPMpolyCentroid = robjects.r('''

GPMpolyCentroid=function(Dir, watershed, DEM, start, end)
{
  library(raster)
  library(rgdal)
  library(rgeos)
  library(utils)
  library(XML)
  library(stats)
  library(stringr)
  library(ncdf4)
  library(sp)
  library(RCurl)
  
  
  url.IMERG.input <- 'https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDF.05/'
  url.TRMM.input <- 'https://disc2.gesdisc.eosdis.nasa.gov/data/TRMM_RT/TRMM_3B42RT_Daily.7'
  myvarIMERG <- 'precipitationCal'
  myvarTRMM <- 'precipitation'
  ####Before getting to work on this function do this check
  if (as.Date(start) >= as.Date('2000-03-01'))
  {
    # Constructing time series based on start and end input days!
    time_period <- seq.Date(from = as.Date(start), to = as.Date(end), by = 'day')

    # Reading cell elevation data (DEM should be in geographic projection)
    watershed.elevation <- raster::raster(DEM)

    # Reading the study Watershed shapefile
    polys <- rgdal::readOGR(dsn=watershed,verbose = F)

    # SWAT climate 'precipitation' master file name
    filenametableKEY<-paste(Dir,myvarTRMM,'Master.txt',sep='')

    # Creating empty lists
    filenameSWAT     <- list()
    filenameSWAT_TXT <- list()
    subbasinCentroids <- list()
    subbasinCentroidsElevation <- list()


    subbasinCentroids<-rgeos::gCentroid(polys,byid = TRUE)@coords
    subbasinCentroidsElevation<-raster::extract(x=watershed.elevation,y=subbasinCentroids,method='simple')
    cell.longlatElev<-data.frame(subbasinCentroids,Elev=subbasinCentroidsElevation)
    names(cell.longlatElev)<-c('LONG','LAT','Elev')


    #### Begin writing SWAT climate input tables
    #### Get the SWAT file names and then put the first record date
    for(jj in 1:dim(polys@data)[1])
    {
      if(dir.exists(Dir)==FALSE){dir.create(Dir)}
      filenameSWAT[[jj]]<-paste(myvarTRMM,as.character(polys@data$GRIDCODE[jj]),sep='')
      filenameSWAT_TXT[[jj]]<-paste(Dir,filenameSWAT[[jj]],'.txt',sep='')
      #write the data begining date once!
      write(x=format(time_period[1],'%Y%m%d'),file=filenameSWAT_TXT[[jj]])
    }


    #### Write out the SWAT grid information master table
    OutSWAT<-data.frame(ID=as.character(polys@data$GRIDCODE),NAME=unlist(filenameSWAT),LAT=cell.longlatElev$LAT,LONG=cell.longlatElev$LONG,ELEVATION=cell.longlatElev$Elev)
    utils::write.csv(OutSWAT,filenametableKEY,row.names = F,quote = F)




    #### Start doing the work!
    #### iterate over days to extract record of either IMERG or TRMMM grids and get the weighted average over the subbasin


    for(kk in 1:length(time_period))
    {
      mon  <- format(time_period[kk],format='%m')
      year <- format(time_period[kk],format='%Y')

      #Decide here whether to use TRMM or IMERG based on data availability
      #Begin with TRMM first which means days before 2014-March-12
      if (time_period[kk] < as.Date('2014-03-12'))
      {
        myurl = paste(paste(url.TRMM.input,year,mon,sep = '/'),'/',sep = '')
        filenames <- RCurl::getURL(myurl)
        filenames <- XML::readHTMLTable(filenames)[[1]]#getting the daily files at each monthly URL
        filenames <- unique(stats::na.exclude(stringr::str_extract(as.character(filenames$Name),'3B42.+(.nc4)')))
        tt<-as.Date(stringr::str_extract(stringr::str_extract(filenames,"20.+.7"),'[0-9]{1,8}'),format='%Y%m%d')
        pp<-tt%in%time_period[kk]
        filenames<-filenames[pp]
        # Extract the ncdf files

        for(ll in 1:length(filenames))# Iterating over each daily data file
        {
          # Downloading the file
          if(dir.exists('./temp/')==FALSE)
          {dir.create('./temp/')}
          utils::download.file(quiet = T,method='curl',url=paste(myurl,filenames[ll],sep = ''),destfile = paste('./temp/',filenames[ll],sep = ''), mode = 'wb', extra = '-n -c ~/.urs_cookies -b ~/.urs_cookies -L')
          # Reading the ncdf file
          nc<-ncdf4::nc_open( paste('./temp/',filenames[ll],sep = '') )
          data<-ncdf4::ncvar_get(nc,myvarTRMM)
          # Reorder the rows
          data<-data[ nrow(data):1, ]
          ###evaluate these values one time!
          if(ll==1 && kk==1)
          {
            ###getting the y values (longitudes in degrees east)
            nc.long.TRMM<-ncdf4::ncvar_get(nc,nc$dim[[1]])
            ####getting the x values (latitudes in degrees north)
            nc.lat.TRMM<-ncdf4::ncvar_get(nc,nc$dim[[2]])
          }
          ncdf4::nc_close(nc)
          ### Save the daily climate data values in a raster
          TRMM<-raster::raster(x=as.matrix(data),xmn=nc.long.TRMM[1],xmx=nc.long.TRMM[NROW(nc.long.TRMM)],ymn=nc.lat.TRMM[1],ymx=nc.lat.TRMM[NROW(nc.lat.TRMM)],crs=sp::CRS('+proj=longlat +datum=WGS84'))
          ## save time by cropping the world raster to the study DEM
          cropTRMM<-raster::crop(x=TRMM,y=watershed.elevation)
          ### Obtaining daily climate values at centroid grids by averaging TRMM grids data with weights within each subbasin as explained earlier
          cell.values<-suppressWarnings(raster::extract(cropTRMM, polys, weights=TRUE, fun=mean))
          cell.values[is.na(cell.values)] <- -99.0 #filling missing data
          ### Looping through the TRMM points and writing out the daily climate data in SWAT format
          for(jj in 1:dim(polys@data)[1])
          {
            write(x=cell.values[jj],filenameSWAT_TXT[[jj]],append=T,ncolumns = 1)
          }

          unlink(x='./temp/', recursive = TRUE)
        }
      }


      else ## Now for dates equal to or greater than 2014 March 12
      {
        myurl = paste(paste(url.IMERG.input,year,mon,sep = '/'),'/',sep = '')
        if(RCurl::url.exists(myurl))
        {
          filenames <- RCurl::getURL(myurl)
          filenames <- XML::readHTMLTable(filenames)[[1]]# Getting the daily files at each monthly URL
          filenames <- unique(stats::na.exclude(stringr::str_extract(as.character(filenames$Name),'3B-DAY.+(.nc4)')))
          tt<-as.Date(stringr::str_extract(stringr::str_extract(filenames,"20.+-"),'[0-9]{1,8}'),format='%Y%m%d')
          pp<-tt%in%time_period[kk]
          filenames<-filenames[pp]
          # Extract the ncdf files

          for(ll in 1:length(filenames))# Iterating over each daily data file
          {
            # Downloading the file
            if(dir.exists('./temp/')==FALSE)
            {dir.create('./temp/')}
            utils::download.file(quiet = T,method='curl',url=paste(myurl,filenames[ll],sep = ''),destfile = paste('./temp/',filenames[ll],sep = ''), mode = 'wb', extra = '-n -c ~/.urs_cookies -b ~/.urs_cookies -L')
            # Reading the ncdf file
            nc<-ncdf4::nc_open( paste('./temp/',filenames[ll],sep = '') )
            data<-ncdf4::ncvar_get(nc,myvarIMERG)
            ###evaluate these values one time!
            if(ll==1)
            {
              ###getting the y values (longitudes in degrees east)
              nc.long.IMERG<-ncdf4::ncvar_get(nc,nc$dim[[1]])
              ####getting the x values (latitudes in degrees north)
              nc.lat.IMERG<-ncdf4::ncvar_get(nc,nc$dim[[2]])
            }

            # Reorder the rows
            data<-data[ nrow(data):1, ]
            ncdf4::nc_close(nc)
            ###save the daily climate data values in a raster
            IMERG<-raster::raster(x=as.matrix(data),xmn=nc.long.IMERG[1],xmx=nc.long.IMERG[NROW(nc.long.IMERG)],ymn=nc.lat.IMERG[1],ymx=nc.lat.IMERG[NROW(nc.lat.IMERG)],crs=sp::CRS('+proj=longlat +datum=WGS84'))
            ## save time by cropping the world raster to the study DEM
            cropIMERG<-raster::crop(x=IMERG,y=watershed.elevation)
            #Obtaining daily climate values at centroid grids by averaging IMERG grids data with weights within each subbasin as explained earlier
            cell.values<-suppressWarnings(raster::extract(cropIMERG, polys, weights=TRUE, fun=mean))
            cell.values[is.na(cell.values)] <- -99.0 #filling missing data

            #loop through the grid points to write out the daily climate data in a SWAT format
            for(jj in 1:dim(polys@data)[1])
            {
              write(x=cell.values[jj],filenameSWAT_TXT[[jj]],append=T,ncolumns = 1)
            }

          }
          unlink(x='./temp/', recursive = TRUE)
        }
      }






    }

  }
  else
  {
    cat('Sorry',paste(format(as.Date(start),'%b'),format(as.Date(start),'%Y'),sep=','),'is out of coverage for TRMM or IMERG data products.','  \n')
    cat('Please pick start date equal to or greater than 2000-Mar-01 to access TRMM and IMERG data products.','  \n')
    cat('Thank you!','  \n')
  }
}
                             
''')