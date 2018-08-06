import rpy2.robjects as robjects

GLDASpolyCentroid = robjects.r('''

GLDASpolyCentroid=function(tempdir, Dir, watershed, DEM, start, end)
{
  setwd(tempdir)
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
  
  url.GLDAS.input <- 'https://hydro1.gesdisc.eosdis.nasa.gov/data/GLDAS/GLDAS_NOAH025_3H.2.1'
  myvar <- 'Tair_f_inst'
  ####Before getting to work on this function do this check
  if (as.Date(start) >= as.Date('2000-01-01'))
  {
    # Constructing time series based on start and end input days!
    time_period <- seq.Date(from = as.Date(start), to = as.Date(end), by = 'day')

    # Reading cell elevation data (DEM should be in geographic projection)
    watershed.elevation <- raster::raster(DEM)

    # Reading the study Watershed shapefile
    polys <- rgdal::readOGR(dsn=watershed,verbose = F)

    # SWAT climate 'air temperature' master file name
    filenametableKEY<-paste(Dir,'temp_Master.txt',sep='')

    # Creating empty lists
    filenameSWAT     <- list()
    filenameSWAT_TXT <- list()
    cell.temp.values <- list()
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
      filenameSWAT[[jj]]<-paste('temp',as.character(polys@data[jj,1]),sep='')
      filenameSWAT_TXT[[jj]]<-paste(Dir,filenameSWAT[[jj]],'.txt',sep='')
      #write the data begining date once!
      write(x=format(time_period[1],'%Y%m%d'),file=filenameSWAT_TXT[[jj]])
    }


    #### Write out the SWAT grid information master table
    OutSWAT<-data.frame(ID=as.character(polys@data[,1]),NAME=unlist(filenameSWAT),LAT=cell.longlatElev$LAT,LONG=cell.longlatElev$LONG,ELEVATION=cell.longlatElev$Elev)
    utils::write.csv(OutSWAT,filenametableKEY,row.names = F,quote = F)

    #### Start doing the work!
    #### iterate over days to extract records at GLDAS grids and get the weighted average over the subbasin


    for(kk in 1:length(time_period))
    {
      julianDate  <- format(as.Date(time_period[kk]),format='%j')
      year <- format(time_period[kk],format='%Y')
      myurl = paste(paste(url.GLDAS.input,year,julianDate,sep = '/'),'/',sep = '')
      filenames <- RCurl::getURL(myurl)
      filenames <- XML::readHTMLTable(filenames)[[1]]#getting the subdaily files at each daily URL
      filenames <- unique(stats::na.exclude(stringr::str_extract(as.character(filenames$Name),'GLDAS.+(.nc4)')))
      # Extract the ncdf files
      for(ll in 1:length(filenames))# Iterating over each subdaily data file
      {

        # Downloading the file
        if(dir.exists('./temp/')==FALSE)
        {dir.create('./temp/')}
        utils::download.file(quiet = T,method='curl',url=paste(myurl,filenames[ll],sep = ''),destfile = paste('./temp/',filenames[ll],sep = ''), mode = 'wb', extra = '-n -c ~/.urs_cookies -b ~/.urs_cookies -L')
        # Reading the ncdf file
        nc<-ncdf4::nc_open( paste('./temp/',filenames[ll],sep = '') )
        ###evaluate these values one time!
        if(ll==1)
        {
          ###getting the y values (longitudes in degrees east)
          nc.long<-ncdf4::ncvar_get(nc,nc$dim[[1]])
          ####getting the x values (latitudes in degrees north)
          nc.lat<-ncdf4::ncvar_get(nc,nc$dim[[2]])
          data<-array(NA,dim=c(length(nc.lat),length(nc.long),length(filenames)))
        }

        data[,,ll]<-matrix(as.vector(ncdf4::ncvar_get(nc,nc$var[[33]])),nrow=length(nc.lat),ncol=length(nc.long),byrow=T)
        # Reorder the rows
        data[,,ll]<-data[nrow(data):1,,ll]
        ncdf4::nc_close(nc)
      }


      # create a stack
      GLDAS<-raster::raster(x=data[,,1],xmn=nc.long[1],xmx=nc.long[NROW(nc.long)],ymn=nc.lat[1],ymx=nc.lat[NROW(nc.lat)],crs=sp::CRS('+proj=longlat +datum=WGS84'))
      for(j in 1:length(filenames))
      {
        rr<-raster::raster(x=data[,,j],xmn=nc.long[1],xmx=nc.long[NROW(nc.long)],ymn=nc.lat[1],ymx=nc.lat[NROW(nc.lat)],crs=sp::CRS('+proj=longlat +datum=WGS84'))
        GLDAS<-raster::stack(x=c(GLDAS,rr),quick=T)
      }
      GLDAS<-raster::dropLayer(GLDAS,1)


      ## save time by cropping the world raster to the study DEM
      cropGLDAS<-raster::crop(x=GLDAS,y=watershed.elevation)
      ### Obtaining subdaily climate values at centroid grids by averaging GLDAS grids data with weights within each subbasin as explained earlier
      ###daily records for each point
      dailytemp<-suppressWarnings(raster::extract(cropGLDAS, polys, weights=TRUE, fun=mean))
      #dailytemp[is.na(dailytemp)] <- -99.0 #filling missing data

      ###obtain minimum daily data over the 3 hrs records
      mindailytemp<-apply(dailytemp,1,min)
      mindailytemp<-mindailytemp - 273.16 #convert to degree C
      mindailytemp[is.na(mindailytemp)] <- -99.0 #filling missing data
      ###same for maximum daily
      maxdailytemp<-apply(dailytemp,1,max)
      maxdailytemp<-maxdailytemp - 273.16 #convert to degree C
      maxdailytemp[is.na(maxdailytemp)] <- -99.0 #filing missing data
      ### Looping through the GLDAS points and writing out the daily climate data in SWAT format
      for(k in 1:dim(polys@data)[1])
      {
        cell.temp.values[[k]]<-paste(maxdailytemp[k],mindailytemp[k],sep=',')
        write(x=cell.temp.values[[k]],filenameSWAT_TXT[[k]],append=T,ncolumns = 1)
      }

      #empty memory and getting ready for next day!
      cell.temp.values<-list()
      rm(data,GLDAS)
      unlink(x='./temp/', recursive = TRUE)
    }



  }


  else
  {
    cat('Sorry',paste(format(as.Date(start),'%b'),format(as.Date(start),'%Y'),sep=','),'is out of coverage for GLDAS data products.','  \n')
    cat('Please pick start date equal to or greater than 2000-Jan-01 to access GLDAS data products.','  \n')
    cat('Thank you!','  \n')
  }

}

 ''')

