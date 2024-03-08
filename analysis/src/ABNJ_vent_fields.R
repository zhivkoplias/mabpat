#install.packages('sf')
#install.packages('tidyverse')

#load libs
library(sf)
library(tidyverse)

#load map
map_hs = sf::read_sf("World_High_Seas_v1_20200826/High_Seas_v1.shp")
map_hs = sf::read_sf("World_ECS_v1_20221013/ecs_v01.shp")
# Transform nc to EPSG 3857 (Pseudo-Mercator, what Google uses)
map_hs = st_transform(map_hs, 3857)

#load file with coordinates
vents <- read.csv(file = 'vent_fields_all_20200325cleansorted.csv')
#select coords
vents$st <- paste('c','(',vents$Latitude,',',vents$Longitude,')')

#counts vents
counter=0
#max length of the fractional part in coords
max_precision = 4
for (i in 1:nrow(vents)) {
  pts_example <- st_point(c(vents$Latitude[i]*(10**max_precision),vents$Longitude[i]*(10**max_precision)))
  in_high_seas = lengths(st_intersects(pts_example, map_hs)) > 0
  if (in_high_seas == TRUE){
    counter=counter+1
    print('hit')
  }
}

#363 vents in high seas (50%), 721 total

