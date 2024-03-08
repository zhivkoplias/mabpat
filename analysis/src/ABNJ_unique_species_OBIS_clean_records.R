library('robis')

candidates <- read.csv('abnj_species_unique_candidates.csv', header=0)

df_abnj <- data.frame(species = c("Species number 1"),
                      observations = c(1),
                      kingdom = c('N/A'),
                      phylum = c('N/A'))

count = 0
for (i in candidates){
  count = count+1
  print(count)
  if (nrow(occurrence(scientificname = i))>0){
  obis_df_all <- occurrence(scientificname = i)
  obis_df_abnj <- occurrence(scientificname = i, areaid = 1)
  if (nrow(obis_df_abnj) == nrow(obis_df_all)){
    print('ABNJ')
    print(i)
    if (is.null(obis_df_abnj$phylum)){
      phylum_value = 'unknown'
    }
    else{ 
      phylum_value = obis_df_abnj$phylum[1]
    }
    #print(ncol((obis_df_abnj)))
    temp_df <- data.frame(species = c(i[1]),
                          observations = c(nrow(obis_df_abnj)),
                          kingdom = c(obis_df_abnj$kingdom[1]),
                          phylum = c(phylum_value))
    df_abnj <- rbind(df_abnj, temp_df)
  }
  else{
    print('WORLDWIDE')
  }
  }
}


write.csv(df_abnj,"true_abnj_species_names.csv", row.names = FALSE)
write.csv(obis_df_abundant_head,"true_abnj_obis_db.csv", row.names = FALSE)
