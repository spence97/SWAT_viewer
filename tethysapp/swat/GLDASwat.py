import rpy2.robjects as robjects

GLDASwat = robjects.r('''

GLDASwat<-function(Dir, watershed, DEM, start, end)
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
    SubdailyTemp     <- list()
    cell.temp.values <- list()
    # The GLDAS data grid information
    # Read start day to extract spatial information and assign elevation data to the grids within the study watersheds

    julianDate  <- format(as.Date(start),format='%j')
    year <- format(as.Date(start),format='%Y')
    myurl = paste(paste(url.GLDAS.input,year,julianDate,sep = '/'),'/',sep = '')
    if(RCurl::url.exists(myurl))
    {
      filenames <- RCurl::getURL(myurl)
      filenames <- XML::readHTMLTable(filenames)[[1]]#getting the sub daily files at each juilan URL
      filenames <- unique(stats::na.exclude(stringr::str_extract(as.character(filenames$Name),'GLDAS.+(.nc4)')))
      # Extract the GLDAS nc4 files for the specific day
      # downloading one file to be able writing Climate info table and gridded file names
      if(dir.exists('./temp/')==FALSE){dir.create('./temp/')}
      utils::download.file(quiet = T,method='curl',url=paste(myurl,filenames[1],sep = ''),destfile = paste('./temp/',filenames[1],sep = ''), mode = 'wb', extra = '-n -c ~/.urs_cookies -b ~/.urs_cookies -L')
      #reading ncdf file
      nc<-ncdf4::nc_open( paste('./temp/',filenames[1],sep = '') )
      #since geographic info for all files are the same (assuming we are working with the same data product)
      ###evaluate these values one time!
      ###getting the y values (longitudes in degrees east)
      nc.long<-ncdf4::ncvar_get(nc,nc$dim[[1]])
      ####getting the x values (latitudes in degrees north)
      nc.lat<-ncdf4::ncvar_get(nc,nc$dim[[2]])
      #extract data
      data<-matrix(as.vector(ncdf4::ncvar_get(nc,nc$var[[33]])),nrow=length(nc.lat),ncol=length(nc.long),byrow=T)
      #reorder the rows
      data<-data[ nrow(data):1, ]
      ncdf4::nc_close(nc)
      ###save the daily climate data values in a raster
      GLDAS<-raster::raster(x=data,xmn=nc.long[1],xmx=nc.long[NROW(nc.long)],ymn=nc.lat[1],ymx=nc.lat[NROW(nc.lat)],crs=sp::CRS('+proj=longlat +datum=WGS84'))
      #obtain cell numbers within the GLDAS raster
      cell.no<-raster::cellFromPolygon(GLDAS, polys)
      #obtain lat/long values corresponding to watershed cells
      cell.longlat<-raster::xyFromCell(GLDAS,unlist(cell.no))
      cell.rowCol <- raster::rowColFromCell(GLDAS,unlist(cell.no))
      points_elevation<-raster::extract(x=watershed.elevation,y=cell.longlat,method='simple')
      study_area_records<-data.frame(ID=unlist(cell.no),cell.longlat,cell.rowCol,Elevation=points_elevation)
      #sp::coordinates (study_area_records)<- ~x+y
      rm(data,GLDAS)
      unlink(x='./temp/', recursive = TRUE)





    }



    #### Begin writing SWAT climate input tables
    #### Get the SWAT file names and then put the first record date
    for(jj in 1:dim(study_area_records)[1])
    {
      if(dir.exists(Dir)==FALSE){dir.create(Dir)}
      filenameSWAT[[jj]]<-paste('temp',study_area_records$ID[jj],sep='')
      filenameSWAT_TXT[[jj]]<-paste(Dir,filenameSWAT[[jj]],'.txt',sep='')
      #write the data begining date once!
      write(x=format(time_period[1],'%Y%m%d'),file=filenameSWAT_TXT[[jj]])
    }


    #### Write out the SWAT grid information master table
    OutSWAT<-data.frame(ID=study_area_records$ID,NAME=unlist(filenameSWAT),LAT=study_area_records$y,LONG=study_area_records$x,ELEVATION=study_area_records$Elevation)
    utils::write.csv(OutSWAT,filenametableKEY,row.names = F,quote = F)

    #### Start doing the work!
    #### iterate over days to extract records at GLDAS grids estabished in 'study_area_records'


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
        data<-matrix(as.vector(ncdf4::ncvar_get(nc,nc$var[[33]])),nrow=length(nc.lat),ncol=length(nc.long),byrow=T)
        # Reorder the rows
        data<-data[ nrow(data):1, ]
        ncdf4::nc_close(nc)
        ### Save the subdaily climate data values in a raster
        GLDAS<-raster::raster(x=data,xmn=nc.long[1],xmx=nc.long[NROW(nc.long)],ymn=nc.lat[1],ymx=nc.lat[NROW(nc.lat)],crs=sp::CRS('+proj=longlat +datum=WGS84'))
        ### Obtaining subdaily climate values at GLDAS grids that has been defined and explained earlier
        cell.values<-as.vector(GLDAS)[study_area_records$ID]
        SubdailyTemp[[ll]]<-cell.values

      }



      ###daily records for each point
      dailytemp<-matrix(unlist(SubdailyTemp),ncol=length(filenames),nrow = dim(study_area_records)[1])
      ###obtain minimum daily data over the 3 hrs records
      mindailytemp<-apply(dailytemp,1,min)
      mindailytemp<-mindailytemp - 273.16 #convert to degree C
      mindailytemp[is.na(mindailytemp)] <- -99.0 #filling missing data
      ###same for maximum daily
      maxdailytemp<-apply(dailytemp,1,max)
      maxdailytemp<-maxdailytemp - 273.16 #convert to degree C
      maxdailytemp[is.na(maxdailytemp)] <- -99.0 #filing missing data
      ### Looping through the GLDAS points and writing out the daily climate data in SWAT format
      for(k in 1:dim(study_area_records)[1])
      {
        cell.temp.values[[k]]<-paste(maxdailytemp[k],mindailytemp[k],sep=',')
        write(x=cell.temp.values[[k]],filenameSWAT_TXT[[k]],append=T,ncolumns = 1)
      }

      #empty memory and getting ready for next day!
      cell.temp.values<-list()
      SubdailyTemp<- list()
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