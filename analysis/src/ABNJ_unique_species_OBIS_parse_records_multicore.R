###install robis
library('robis')

###save areaids
ids <- c(1,2,3,4,5,7,8,9,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,36,37,38,39,40,41,42,43,44,45,46,47,48,49,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,91,92,93,94,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,167,168,169,170,171,172,173,174,175,177,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,224,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,266,278,279,280,281,282)
#ids <- c(8,9,17,266,278,279,280,281,282)
#ids <- c(9)
#ids <- 1
#ids <- c(2,3,4)
#dir to save output
#outfile = 'obis_not_abnj_species_test.csv'
setwd("~/data/mgr/data/processed/obis_records")

#initialize long list
all_abnj_species <- vector("list", 50000)

###example of function to retrieve records
counter=1
run_OBIS_species_count <- function(){
  for (name in ids){
    print(sprintf("Now processing areaid: %i", name))
    temp=counter
    records <- occurrence(areaid = name)
    
    records <- records[!(is.na(records$species)), ]
    records <- records[records$absence != TRUE, ]
    #records <- records[(records$marine==1) & (records$brackish==0) & (records$terrestrial==0), ]
    
    unique_species_names <- unique(records$scientificName)
    
    temp = print(length(unique_species_names))
    all_abnj_species[counter:(temp+counter)] <- unique_species_names
    
    all_abnj_species.df <- do.call("rbind", lapply(all_abnj_species, as.data.frame))
    #all_abnj_species.df$`X[[i]]` <- keep_singles(all_abnj_species.df$`X[[i]]`)
    write.csv(all_abnj_species.df, outfile, row.names = FALSE, col.names = FALSE)
    
    counter <- temp+counter
    gc()
  }
}

#run_OBIS_species_count()

#function for multi-processing
run_cluster <- function(){
  library(parallel)
  no_cores <- detectCores()/2
  #no_cores <- no_cores + 6
  clust <- makeCluster(no_cores, type="FORK", outfile = 'logs_australia.txt')
  parLapply(clust,ids, function(name) {
    print(sprintf("Now processing areaid: %i", name))
    records <- occurrence(areaid = name)
    
    records <- records[!(is.na(records$species)), ]
    records <- records[records$absence != TRUE, ]
    
    unique_species_names <- unique(records$scientificName)
    
    print(length(unique_species_names))
    all_abnj_species.df <- do.call("rbind", lapply(unique_species_names, as.data.frame))
    write.csv(all_abnj_species.df, paste(substring(name, c(1,7)), collapse=".tsv"), row.names = FALSE, col.names = FALSE)
    print(sprintf("DONE processing areaid: %i", name))
    gc()})
  stopCluster(clust)
}

#run function
run_cluster()
