import rpy2.robjects as robjects

GPMswat = robjects.r('''

GPMswat=function(Dir, watershed, DEM, start, end)
{

  library(raster)
  library(ncdf4)
  library(RCurl)
  library(stringr)
  library(rgdal)
  library(curl)
  library(XML)
  library(utils)
  library(sp)
  library(methods)
  library(stats)
             
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
    closestSiteVec   <- list()
    minDistVec       <- list()



    # The IMERG data grid information
    # Read a dummy day to extract spatial information and assign elevation data to the grids within the study watersheds

    DUMMY_DATE <- as.Date('2014-05-01')

    mon  <- format(DUMMY_DATE,format='%m')
    year <- format(DUMMY_DATE,format='%Y')
    myurl = paste(paste(url.IMERG.input,year,mon,sep = '/'),'/',sep = '')
    if(RCurl::url.exists(myurl))
    {
      filenames <- RCurl::getURL(myurl)
      filenames <- XML::readHTMLTable(filenames)[[1]]#getting the daily files at each monthly URL
      filenames <- unique(stats::na.exclude(stringr::str_extract(as.character(filenames$Name),'3B-DAY.+(.nc4)')))
      # Extract the IMERG nc4 files for the specific month
      # trying here the first day since I am only interested on grid locations
      # downloading one file
      if(dir.exists('./temp/')==FALSE){dir.create('./temp/')}
      utils::download.file(quiet = T,method='curl',url=paste(myurl,filenames[1],sep = ''),destfile = paste('./temp/',filenames[1],sep = ''), mode = 'wb', extra = '-n -c ~/.urs_cookies -b ~/.urs_cookies -L')
      #reading ncdf file
      nc<-ncdf4::nc_open( paste('./temp/',filenames[1],sep = '') )
      #since geographic info for all files are the same (assuming we are working with the same data product)
      ###evaluate these values one time!
      ###getting the y values (longitudes in degrees east)
      nc.long.IMERG<-ncdf4::ncvar_get(nc,nc$dim[[1]])
      ####getting the x values (latitudes in degrees north)
      nc.lat.IMERG<-ncdf4::ncvar_get(nc,nc$dim[[2]])
      #extract data
      data<-ncdf4::ncvar_get(nc,myvarIMERG)
      #reorder the rows
      data<-data[ nrow(data):1, ]
      ncdf4::nc_close(nc)
      ###save the daily climate data values in a raster
      IMERG<-raster::raster(x=as.matrix(data),xmn=nc.long.IMERG[1],xmx=nc.long.IMERG[NROW(nc.long.IMERG)],ymn=nc.lat.IMERG[1],ymx=nc.lat.IMERG[NROW(nc.lat.IMERG)],crs=sp::CRS('+proj=longlat +datum=WGS84'))
      #obtain cell numbers within the IMERG raster
      cell.no<-raster::cellFromPolygon(IMERG, polys)
      #obtain lat/long values corresponding to watershed cells
      cell.longlat<-raster::xyFromCell(IMERG,unlist(cell.no))
      cell.rowCol <- raster::rowColFromCell(IMERG,unlist(cell.no))
      points_elevation<-raster::extract(x=watershed.elevation,y=cell.longlat,method='simple')
      study_area_records_IMERG<-data.frame(ID=unlist(cell.no),cell.longlat,cell.rowCol,Elevation=points_elevation)
      sp::coordinates (study_area_records_IMERG)<- ~x+y
      rm(data,IMERG)
      unlink(x='./temp/', recursive = TRUE)
    }

    # The TRMM data grid information
    # Use the same dummy date defined above since TRMM has data up to present with less accurancy. The recomendation is to use IMERG data from 2014-03-12 and onward!
    # update my url with TRMM information
    myurl = paste(paste(url.TRMM.input,year,mon,sep = '/'),'/',sep = '')

    if(RCurl::url.exists(myurl))
    {
      filenames <- RCurl::getURL(myurl)
      filenames <- XML::readHTMLTable(filenames)[[1]]# getting the daily files at each monthly URL
      filenames <- unique(stats::na.exclude(stringr::str_extract(as.character(filenames$Name),'3B42.+(.nc4)')))
      # Extract the TRMM nc4 files for the specific month
      # trying here the first day since I am only interested on grid locations
      # downloading one file
      if(dir.exists('./temp/')==FALSE){dir.create('./temp/')}
      utils::download.file(quiet = T,method='curl',url=paste(myurl,filenames[1],sep = ''),destfile = paste('./temp/',filenames[1],sep = ''), mode = 'wb', extra = '-n -c ~/.urs_cookies -b ~/.urs_cookies -L')
      #reading ncdf file
      nc<-ncdf4::nc_open( paste('./temp/',filenames[1],sep = '') )
      #since geographic info for all files are the same (assuming we are working with the same data product)
      ###evaluate these values one time!
      ###getting the y values (longitudes in degrees east)
      nc.long.TRMM<-ncdf4::ncvar_get(nc,nc$dim[[1]])
      ####getting the x values (latitudes in degrees north)
      nc.lat.TRMM<-ncdf4::ncvar_get(nc,nc$dim[[2]])
      #gettig the climate data
      data<-ncdf4::ncvar_get(nc,myvarTRMM)
      #reorder the rows
      data<-data[ nrow(data):1, ]
      ncdf4::nc_close(nc)
      ###save the daily climate data values in a raster
      TRMM<-raster::raster(x=as.matrix(data),xmn=nc.long.TRMM[1],xmx=nc.long.TRMM[NROW(nc.long.TRMM)],ymn=nc.lat.TRMM[1],ymx=nc.lat.TRMM[NROW(nc.lat.TRMM)],crs=sp::CRS('+proj=longlat +datum=WGS84'))
      #obtain cell numbers within the TRMM raster
      cell.no<-raster::cellFromPolygon(TRMM, polys)
      #obtain lat/long values corresponding to watershed cells
      cell.longlat<-raster::xyFromCell(TRMM,unlist(cell.no))
      cell.rowCol <- raster::rowColFromCell(TRMM,unlist(cell.no))
      cell.values<-as.vector(TRMM)[unlist(cell.no)]
      study_area_records_TRMM<-data.frame(TRMM_ID=unlist(cell.no),cell.longlat,cell.rowCol)
      sp::coordinates (study_area_records_TRMM)<- ~x+y
      rm(data,TRMM)
      unlink(x='./temp/', recursive = TRUE)
    }


    # creating a similarity table that connects IMERG and TRMM grids
    # calculate euclidean distances to know how to connect TRMM grids with IMERG grids
    for (i in 1 : nrow(study_area_records_IMERG))
    {
      distVec <- sp::spDistsN1(study_area_records_TRMM,study_area_records_IMERG[i,])
      minDistVec[[i]] <- min(distVec)
      closestSiteVec[[i]] <- which.min(distVec)
    }

    PointAssignIDs <- methods::as(study_area_records_TRMM[unlist(closestSiteVec),]$TRMM_ID,'numeric')
    PointsAssignCol <- methods::as(study_area_records_TRMM[unlist(closestSiteVec),]$col,'numeric')
    PointsAssignRow <- methods::as(study_area_records_TRMM[unlist(closestSiteVec),]$row,'numeric')

    FinalTable = data.frame(sp::coordinates(study_area_records_IMERG),ID=study_area_records_IMERG$ID,row=study_area_records_IMERG$row,col=study_area_records_IMERG$col,Elevation=study_area_records_IMERG$Elevation,
                            CloseTRMMIndex=PointAssignIDs,Distance=unlist(minDistVec),TRMMCol=PointsAssignCol,TRMMRow=PointsAssignRow)

    #### Begin writing SWAT climate input tables
    #### Get the SWAT file names and then put the first record date
    for(jj in 1:dim(FinalTable)[1])
    {
      if(dir.exists(Dir)==FALSE){dir.create(Dir)}
      filenameSWAT[[jj]]<-paste(myvarTRMM,FinalTable$ID[jj],sep='')
      filenameSWAT_TXT[[jj]]<-paste(Dir,filenameSWAT[[jj]],'.txt',sep='')
      #write the data begining date once!
      write(x=format(time_period[1],'%Y%m%d'),file=filenameSWAT_TXT[[jj]])
    }


    #### Write out the SWAT grid information master table
    OutSWAT<-data.frame(ID=FinalTable$ID,NAME=unlist(filenameSWAT),LAT=FinalTable$y,LONG=FinalTable$x,ELEVATION=FinalTable$Elevation)
    utils::write.csv(OutSWAT,filenametableKEY,row.names = F,quote = F)




    #### Start doing the work!
    #### iterate over days to extract record at IMERG grids estabished in 'FinalTable'


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
          #if(<=as.Date(end))
          #{
          # Downloading the file
          if(dir.exists('./temp/')==FALSE)
          {dir.create('./temp/')}
          utils::download.file(quiet = T,method='curl',url=paste(myurl,filenames[ll],sep = ''),destfile = paste('./temp/',filenames[ll],sep = ''), mode = 'wb', extra = '-n -c ~/.urs_cookies -b ~/.urs_cookies -L')
          # Reading the ncdf file
          nc<-ncdf4::nc_open( paste('./temp/',filenames[ll],sep = '') )
          data<-ncdf4::ncvar_get(nc,myvarTRMM)
          # Reorder the rows
          data<-data[ nrow(data):1, ]
          ncdf4::nc_close(nc)
          ### Save the daily climate data values in a raster
          TRMM<-raster::raster(x=as.matrix(data),xmn=nc.long.TRMM[1],xmx=nc.long.TRMM[NROW(nc.long.TRMM)],ymn=nc.lat.TRMM[1],ymx=nc.lat.TRMM[NROW(nc.lat.TRMM)],crs=sp::CRS('+proj=longlat +datum=WGS84'))
          ### Obtaining daily climate values at TRMM grids near the IMERG grids that has been defined and explained earlier
          cell.values<-as.vector(TRMM)[FinalTable$CloseTRMMIndex]
          cell.values[is.na(cell.values)] <- -99.0 #filling missing data
          ### Looping through the TRMM points and writing out the daily climate data in SWAT format
          for(jj in 1:dim(FinalTable)[1])
          {
            write(x=cell.values[jj],filenameSWAT_TXT[[jj]],append=T,ncolumns = 1)
          }
          #}
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
            # Reorder the rows
            data<-data[ nrow(data):1, ]
            ncdf4::nc_close(nc)
            ###save the daily climate data values in a raster
            IMERG<-raster::raster(x=as.matrix(data),xmn=nc.long.IMERG[1],xmx=nc.long.IMERG[NROW(nc.long.IMERG)],ymn=nc.lat.IMERG[1],ymx=nc.lat.IMERG[NROW(nc.lat.IMERG)],crs=sp::CRS('+proj=longlat +datum=WGS84'))

            #obtain daily climate values at cells bounded with the study watershed (extract values from a raster)
            cell.values<-as.vector(IMERG)[FinalTable$ID]
            cell.values[is.na(cell.values)] <- -99.0 #filling missing data

            #This will get me the mean precipiation averaged over the watershed (this is not a weighted mean)
            #v <- extract(IMERG, polys,weights=T,cellnumbers=T,df=T,normalizeWeights=T,sp=T,fun='mean')

            #loop through the grid points to write out the daily climate data in a SWAT format
            for(jj in 1:dim(FinalTable)[1])
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








