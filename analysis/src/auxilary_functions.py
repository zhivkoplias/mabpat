def get_company(journal):
    
    # Sometimes there is a COMMENT section between JOURNAL & FEATURES... 
    # if so, journal should be cut before it
    if 'COMMENT' in journal:
        journal = journal[:journal.index('COMMENT')]
    
    journal_lines = journal.splitlines()
    
    # The first line is the Patent + Date string
    # If there is company info, this is on the following lines
    if len(journal_lines) > 1: 
        # aggregate together all company lines into one string 
        company = ' '.join([line.strip() for line in journal_lines[1:]]) 
    else: 
        company = None # No company info 
    return company 
    
def valid_sequence(column):
    all_nucs = 'agtc'
    
    if all(i in all_nucs for i in column):
        return 1
    else:
        return None
    
def get_patent(jstr):
    import re
    
    pats = re.findall('(: .+?(?=(\s\d*-\w\d*)))', jstr)
    if not pats:
        print(pats)
        return None
    else:
        pats = pats[0]
        joiner = "".join
        return "".join(list(filter(None, [joiner(words) for words in pats])))[2::].replace(" ", "").replace("-", "")
    
def get_patent_url(jstr):

    return "https://patents.google.com/patent/"+ jstr + "/en?oq=" + jstr[2::]


def get_patent_info(patent_url):

    response = requests.get(patent_url)
    txt = response.content
    soup = BeautifulSoup(txt,'html.parser')

    for tag in soup.findAll(True):
        
        patent_abstract = None
        
        if tag.name == 'title':
            #patent_name = tag.text.split('-')[1]
            patent_name = tag.text
            
    for tag in soup.findAll(True):
        
        if tag.name == 'abstract':
            patent_abstract = tag.text

    return patent_name, patent_abstract


def loadall(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break
                
                
def wordcloud_for_go(pandas_df_column):
    
    comment_words = ''
    stopwords = set(STOPWORDS)
    more_stopwords = ['GO:', '[', ']', 'go', 'nan']

    for word in more_stopwords:
        stopwords.add(word)


    #iterate through titles
    for val in pandas_df_column:

        # typecaste each val to string
        val = str(val)

        # split the value
        tokens = val.split()

        # Converts each token into lowercase
        for i in range(len(tokens)):
            tokens[i] = tokens[i].lower()

        comment_words += " ".join(tokens)+" "
    
    wordcloud = WordCloud(width = 800, height = 800,
                    background_color ='white',
                    stopwords = stopwords,
                    min_font_size = 10).generate(comment_words)
    
    return wordcloud


def get_species_blast_search(jstr):
    pats = re.findall('(?<=OS=).?[^{(,OX}]+', jstr)
    if not pats:
        print(pats)
        return None
    else:
        pats = pats[0]
        return pats
    

def split_dataframe(df, chunk_size = 1000): 
    chunks = list()
    num_chunks = len(df) // chunk_size + 1
    for i in range(num_chunks):
        chunks.append(df[i*chunk_size:(i+1)*chunk_size])
    return chunks


def get_pd_df_uniprot(df_chunks):
    
    import sys
    from io import StringIO
    
    lst_with_results = []
    
    for i in range(len(df_chunks)):
        temp_df = df_chunks[i]
        accessions = temp_df['uniprot_id']
        joined = ",".join(accessions)
        
        r = get_url(f"{WEBSITE_API}/uniprotkb/accessions?accessions={joined}&fields=id,accession,length,go,go_f,go_p,go_c,go_id,keyword",
           headers={"Accept": "text/plain; format=tsv"})
        
        TESTDATA = StringIO(r.text)
        temp_df_uniprot = pd.read_csv(TESTDATA, sep="\t")
        
        lst_with_results.append(temp_df_uniprot)
        
    df_uniprot = pd.concat(lst_with_results)
    
    return df_uniprot


def get_patent_id(x):
    
    return x.split('_')[0]

def filter_company_names(pandas_df):
    
    pandas_df['patent_num'] = None
    pandas_df['patent_num'] = pandas_df.journal.apply(lambda x: get_patent(x))
    pandas_df['patent_url'] = pandas_df.patent_num.apply(lambda x: get_patent_url(x))
    pandas_df['origin'] = pandas_df['origin'].str.lower()
    pandas_df['company'] = pandas_df['company'].str.upper()
    
    
    for _ in range(2):
        
        #DSM IP ASSETS BV
        pandas_df['company'] = pandas_df['company'].str.replace(r'DSM IP ASSETS B V +', 'DSM IP ASSETS BV', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'DSM IP ASSETS B.V+', 'DSM IP ASSETS BV', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'DSM IP ASSETS B V+', 'DSM IP ASSETS BV', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'DSM IP ASSETS BV.+', 'DSM IP ASSETS BV', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'MARTEK BIOSCIENCES.+', 'MARTEK BIOSCIENCES', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'MARTEK BIOSCIENCES', 'DSM IP ASSETS BV', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'MARTECK BIOSCIENCES', 'DSM IP ASSETS BV', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'DSM NUTRITIONAL PRODUCT.+', 'DSM IP ASSETS BV', regex=True)
        
        #AERA HERPEUTICS
        pandas_df['company'] = pandas_df['company'].str.replace(r'VNV NEWCO', 'AERA HERPEUTICS', regex=True)
        
        #AJINOMOTO
        pandas_df['company'] = pandas_df['company'].str.replace(r'AJINOMOTO CO.+', 'AJINOMOTO CO INC', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'AJINOMOTO.+', 'AJINOMOTO', regex=True)
        
        #BAYER
        pandas_df['company'] = pandas_df['company'].str.replace(r'BAYER.+', 'BAYER', regex=True)
        #pandas_df['company'] = pandas_df['company'].str.replace(r'MONSANTO TECHNOLOGY.+', 'MONSANTO TECHNOLOGY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'MONSANTO.+', 'BAYER', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'CALGENE LLC', 'BAYER', regex=True)
        
        #NOVOZYMES
        pandas_df['company'] = pandas_df['company'].str.replace(r'NOVOZYMES.+', 'NOVOZYMES', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'ORGANOBALANC.+', 'NOVOZYMES', regex=True)
        
        
        #BASF
        pandas_df['company'] = pandas_df['company'].str.replace(r'VERENIUM.+', 'VERENIUM', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'VERENIUM', 'BASF', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'CROPDESIGN.+', 'CROPDESIGN', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'CROPDESIGN', 'BASF', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'BASF.+', 'BASF', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'Metanomics.+', 'BASF', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'MEGANOMICS.+', 'BASF', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SUNGENE GMBH', 'BASF', regex=True)
        pandas_df.loc[pandas_df['company'].str.contains('METANOMICS', case=False), 'company'] = 'BASF'
        pandas_df['company'] = pandas_df['company'].str.replace(r'METANOMICS GMB.+', 'BASF', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SUNGENE GMBH', 'BASF', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SUNGENE GMBH',
                                                                'BASF', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'DIVERSA CORP',
                                                                'BASF', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'DIVERSA INC',
                                                                'BASF', regex=True)
        
        
        
        #CSIRO
        pandas_df['company'] = pandas_df['company'].str.replace(r'COMMW SCIENT IND RES ORG.+', 'CSIRO', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'COMMONWEALTH SCIENTIFIC AND INDUSTRIAL RESEARCH.+', 'CSIRO', regex=True)
        
        #HOLOGIC
        pandas_df['company'] = pandas_df['company'].str.replace(r'THIRD WAVE TECHNOLOGIES.+', 'THIRD WAVE TECHNOLOGIES', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THIRD WAVE TECHNOLOGIES', 'HOLOGIC INC', regex=True)
        
        #SEIKAGAKU
        pandas_df['company'] = pandas_df['company'].str.replace(r'SEIKAGAK.+', 'SEIKAGAKU CORPORATION', regex=True)
        
        #CORBION
        pandas_df['company'] = pandas_df['company'].str.replace(r'SOLAZYME.+', 'SOLAZYME', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SOLAZYME', 'TERRAVIA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'TERRAVIA HOLDINGS.+', 'TERRAVIA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'TERRAVIA', 'CORBION', regex=True)
        
        #PROMEGA
        pandas_df['company'] = pandas_df['company'].str.replace(r'PROMEGA COR.+', 'PROMEGA CORPORATION', regex=True)
        
        #SCRIPPTS
        pandas_df['company'] = pandas_df['company'].str.replace(r'SCRIPPS RESEARCH INST.+', 'THE SCRIPPS RESEARCH INSTITUTE', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE THE SCRIPPS RESEARCH.+', 'SCRIPPS RESEARCH INSTITUTE', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE SCRIPPS RESEARCH.+', 'SCRIPPS RESEARCH INSTITUTE', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE SCRIPPS RES INST [US]',
                                                                'SCRIPPS RESEARCH INSTITUTE', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE SCRIPPS RES INST [US]',
                                                                'SCRIPPS RESEARCH INSTITUTE', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SCRIPS RES INST [US]',
                                                                'SCRIPPS RESEARCH INSTITUTE', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE SCRIPPS RES INST [US]',
                                                                'SCRIPPS RESEARCH INSTITUTE', regex=True)
        
        
        
        #VIRIDOS
        pandas_df['company'] = pandas_df['company'].str.replace(r'SYNTHETIC GENOMICS.+', 'SYNTHETIC GENOMICS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SYNTHETIC GENOMICS', 'VIRIDOS', regex=True)
        
        #CHEVRON
        pandas_df['company'] = pandas_df['company'].str.replace(r'LS9', 'RENEWABLE ENERGY GROUP', regex=True)    
        pandas_df['company'] = pandas_df['company'].str.replace(r'REG LIFE SCIENCE.+', 'RENEWABLE ENERGY GROUP', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'RENEWABLE ENERGY GROUP', 'CHEVRON', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'REG LIFE SCIENCES.+', 'REG LIFE SCIENCES', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'REG LIFE SCIENCES', 'CHEVRON', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'CHEVRO.+', 'CHEVRON', regex=True)
        
        #CHISSO CORPORATION
        pandas_df['company'] = pandas_df['company'].str.replace(r'JNC CORPORATI.+', 'CHISSO CORPO', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'CHISSO COR.+', 'CHISSO CORPORATION', regex=True)
        
        
        #AIST
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL INSTITUTE OF ADVANCED INDUSTRIAL SCIENCE AND.+', 'AIST', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'AIST [JP]', 'AIST', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'AIST [JP].+', 'AIST', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'ADVANCED INDUSTRIAL SCIENCE AND TECHNOLOGY', 'AIST', regex=True)
        
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'MARINE BIOTECHNOLOGY INST.+', 'MARINE BIOTECHNOLOGY INST', regex=True)
        
        #IFF
        pandas_df['company'] = pandas_df['company'].str.replace(r'BUTAMAX.+', 'BUTAMAX', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'BUTAMAX', 'IFF', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'AMBRX INC.+', 'AMBRX INC', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'AMBRX.+', 'AMBRX', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'YEDA.+', 'YEDA', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'DANISCO.+', 'DANISCO', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'DANISCO', 'DU PONT', regex=True)
        
        #DU PONT
        pandas_df['company'] = pandas_df['company'].str.replace(r'.+DU PONT DE NEMOROUS AND COMPANY.+', 'DU PONT DE NEMOROUS AND COMPANY', regex=True)
        pandas_df.loc[pandas_df['company'].str.contains('DU PONT DE NEMOROUS', case=False), 'company'] = 'DU PONT'
        pandas_df.loc[pandas_df['company'].str.contains('DU PONT', case=False), 'company'] = 'DU PONT'
        pandas_df.loc[pandas_df['company'].str.contains('DUPONT', case=False), 'company'] = 'DU PONT'
        
        
        pandas_df.loc[pandas_df['company'].str.contains('GENOMAR', case=False), 'company'] = 'GENOMAR'
        pandas_df.loc[pandas_df['company'].str.contains('MEDLIN LINDA \[GB\]', case=False), 'company'] = 'MICROBIA ENVIRONMENT'
        pandas_df.loc[pandas_df['company'].str.contains('GENEFRONTIER CORPORATION', case=False), 'company'] = 'GENEFRONTIER CORPORATION'
        
        #UNIVERSITY OF NEW SOUTH WALES
        pandas_df['company'] = pandas_df['company'].str.replace(r'NEWSOUTH INNOVATIONS.+', 'NEWSOUTH INNOVATIONS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'NEWSOUTH INNOVATIONS', 'UNIVERSITY OF NEW SOUTH WALES', regex=True)
        
        #UNI OF UTAH
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIVERSITY OF UTAH.+', 'UNIVERSITY OF UTAH', regex=True)
        
        #EW GROUP GMBH
        pandas_df['company'] = pandas_df['company'].str.replace(r'AQUA(\s)GEN.+', 'AQUAGEN', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'AQUAGEN.+', 'AQUAGEN', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'AQUAGEN', 'EW GROUP GMBH', regex=True)
         
        #AMBREX
        pandas_df['company'] = pandas_df['company'].str.replace(r'AMBR(\s)X.+', 'AMBREX', regex=True)
        
        #EVOLVA
        pandas_df['company'] = pandas_df['company'].str.replace(r'EVOLVA(\s)X.+', 'EVOLVA', regex=True)
        
        #UNIVERSITY OF CALIFORNIA
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV CALIFORNI', 'THE REGENTS OF THE UNIVERSITY OF CALIFORNIA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE REGENTS OF THE UNIVERSITY OF CALIFORNI.+', 'THE REGENTS OF THE UNIVERSITY OF CALIFORNIA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'REGENTS OF THE UNIVERSITY OF CALIFORNI.+', 'THE REGENTS OF THE UNIVERSITY OF CALIFORNIA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE THE THE REGENTS OF THE UNIVERSITY OF CALIFORNIA', 'THE REGENTS OF THE UNIVERSITY OF CALIFORNIA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE THE REGENTS OF THE UNIVERSITY OF CALIFORNIA', 'THE REGENTS OF THE UNIVERSITY OF CALIFORNIA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE REGENTS OF THE UNIVERSITY OF CALIFORNIA', 'UNIVERSITY OF CALIFORNIA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE REGENTS OF THE UNIVERSITY OF CALIFORNIA', 'UNIVERSITY OF CALIFORNIA', regex=True)
        
        
        
        #CHINA
        pandas_df['company'] = pandas_df['company'].str.replace(r'SYNGENT.+',
                                                                'SYNGENTA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SYNGENTA PARTICIPATIONS.+', 'SYNGENTA PARTICIPATIONS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SYNGENTA PARTICIPATIONS', 'GOVERNMENT OF CHINA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SYNGENTA', 'GOVERNMENT OF CHINA', regex=True)
        
        
        #ODYSSEY THERA
        pandas_df['company'] = pandas_df['company'].str.replace(r'ODYSSEY THERA IN.+', 'ODYSSEY THERAPEUTICS', regex=True)
        
        #AIST
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE AIST', 'AIST', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'AIST [JP]',
                                                                'AIST', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'DIRECTOR GENERAL OF AIST',
                                                                'AIST', regex=True)

        pandas_df['company'] = pandas_df['company'].str.replace(r'AGENCY OF IND SCIENCE & TECHNO.+',
                                                                'AIST', regex=True)
        
        #JST
        pandas_df['company'] = pandas_df['company'].str.replace(r'JAPAN SCIENCE AND TECHNOLOGY COR.+',
                                                                'JST', regex=True)
        
        
        #KOREA INSTITUTE OF OCEAN SCIENCE & TECHNOLOGY
        pandas_df['company'] = pandas_df['company'].str.replace(r'KOREA INSTITUTE OF OCEAN SCIENCE & TECHNOLOG.+',
                                                                'KOREA INSTITUTE OF OCEAN SCIENCE & TECHNOLOGY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'KOREA INSTITUTE OF OCEAN SCIENCE AND TECHNOLOG.+',
                                                                'KOREA INSTITUTE OF OCEAN SCIENCE & TECHNOLOGY', regex=True)
        
        #CHISSO CORPORATION
        pandas_df['company'] = pandas_df['company'].str.replace(r'CHISSO CORPORATION', 'CHISSO CORPORATION; OSAKA; JP;', regex=True)
        
        #TAKARA HOLDINGS
        pandas_df['company'] = pandas_df['company'].str.replace(r'TAKARA BIO IN.+', 'TAKARA HOLDINGS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'CLONTECH LABORATORIE.+',
                                                                'CLONTECH LABORATORIES', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'CLONTECH LABORATORIES', 'TAKARA HOLDINGS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'TAKARA SHUZ.+',
                                                                'TAKARA HOLDINGS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'TAKARA.+',
                                                                'TAKARA HOLDINGS', regex=True)
        
        #SEIKAGAKU CORPORATION
        pandas_df['company'] = pandas_df['company'].str.replace(r'SEIKAGAKU CORPORATIO.+', 'SEIKAGAKU CORPORATION', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SEIKAGAKU CORP', 'SEIKAGAKU CORPORATION', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SEIKAGAKU CORPORATIONORATION', 'SEIKAGAKU CORPORATION', regex=True)
        
        
        #KOREA UNIVERSITY RESEARCH AND BUSINESS FOUNDATION
        pandas_df['company'] = pandas_df['company'].str.replace(r'KOREA UNIVERSITY RESEARCH AND BUSINESS FOU.+',
                                                                'KOREA UNIVERSITY RESEARCH AND BUSINESS FOUNDATION', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'KOREA UNIVERSITY RESEARCH AND BUSINESS FOUNDATION, SEJONG CAMPUS',
                                                                'KOREA UNIVERSITY RESEARCH AND BUSINESS FOUNDATION', regex=True)
        
        #RIKEN (Institute)
        pandas_df['company'] = pandas_df['company'].str.replace(r'RIKE.+',
                                                                'RIKEN', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'RIKEN ET AL',
                                                                'RIKEN', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE INSTITUTE OF PHYSICAL AND CHEMICAL RESEARCH',
                                                                'RIKEN', regex=True)
        
        
        #JAPAN TOBACCO INC
        pandas_df['company'] = pandas_df['company'].str.replace(r'JAPAN TOBACCO INC,TAKDAYUKI IMANAKA',
                                                                'JAPAN TOBACCO INC', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'JAPAN TOBACCO IN.+',
                                                                'JAPAN TOBACCO INC', regex=True)
    
        
        #SUMITOMO CHEMICAL CO LTD
        pandas_df['company'] = pandas_df['company'].str.replace(r'SUMITOMO CHEMICAL COMPANY, LIMITED; TOKYO',
                                                                'SUMITOMO CHEMICAL CO LTD', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SUMITOMO CHEMICA.+',
                                                                'SUMITOMO CHEMICAL', regex=True)
        
        #OSAKA UNIVERSITY
        pandas_df['company'] = pandas_df['company'].str.replace(r'OSAKA UNIVERSITY; OSAKA',
                                                                'OSAKA UNIVERSITY', regex=True)
        
        #UNIVERSITY OF UTAH
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE UNIVERSITY OF UTAH',
                                                                'UNIVERSITY OF UTAH', regex=True)
        
        #JAPAN SCIENCE AND TECHNOLOGY AGENCY
        pandas_df['company'] = pandas_df['company'].str.replace(r'JAPAN SCIENCE AND TECHNOLOGY AGEN.+',
                                                                'JAPAN SCIENCE AND TECHNOLOGY AGENCY', regex=True)
        
        #CENTRE NATIONAL DE LA RECHERCHE SCIENTIFIQUE
        pandas_df['company'] = pandas_df['company'].str.replace(r'CENTRE NATIONAL DE LA RECHERCHE SCIENTIFIQU.+',
                                                                'CNRS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'CENTRE NAT RECH SCIEN.+',
                                                                'CNRS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'LE CNR.+',
                                                                'CNRS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'CENTRE NAT RECH SCIEN.+',
                                                                'CNRS', regex=True)
        
        
        
        #THE UNIVERSITY OF YORK (GB)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE UNIVERSITY OF YOR.+',
                                                                'THE UNIVERSITY OF YORK', regex=True)
        
        
        #NATIONAL UNIVERSITY CORPORATION HOKKAIDO UNIVERSITY
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL UNIVERSITY CORPORATION HOKKAIDO UNIVERSIT.+',
                                                                'HOKKAIDO UNIVERSITY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'HOKKAIDO UNIVERSIT.+',
                                                                'HOKKAIDO UNIVERSITY', regex=True)
        
        #TOYAMA PREFECTURE
        pandas_df['company'] = pandas_df['company'].str.replace(r'TOYAMA PREFECTUR.+',
                                                                'TOYAMA PREFECTURE', regex=True)
        
        #REPUBLIC OF KOREA(MANAGEMENT : RURAL DEVELOPMENT ADMINISTRATION)
        pandas_df['company'] = pandas_df['company'].str.replace(r'REPUBLIC OF KORE.+',
                                                                'REPUBLIC OF KOREA', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'REPUBLIC OF KOREA(MANAGEMENT : RURAL DEVELOPMENT ADMINISTRATION)|POSTECH ACADEMY-INDUSTRY FOUNDATION',
                                                                'REPUBLIC OF KOREA', regex=True)
        
        #EVOLVA
        pandas_df['company'] = pandas_df['company'].str.replace(r'EVOLV.+',
                                                                'EVOLVA', regex=True)
        #AGILIENT TECHNOLOGIES
        pandas_df['company'] = pandas_df['company'].str.replace(r'STRATAGEN.+',
                                                                'STRATAGENE', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'STRATAGENE',
                                                                'AGILENT TECHNOLOGIES', regex=True)   
        
        #TOKYO UNIVERSITY OF MARINE SCIENCE AND TECHNOLOGY
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL UNIVERSITY CORPORATION TOKYO UNIVERSITY OF MARINE SCIENCE AND TECHNOLOGY',
                                                                'TOKYO UNIVERSITY OF MARINE SCIENCE AND TECHNOLOGY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL UNIVERSITY CORPORATION TOKYO UNIVERSITY OF MARINE SCIENCE AND TECHNOLOGY,OITA PREFECTURE',
                                                                'TOKYO UNIVERSITY OF MARINE SCIENCE AND TECHNOLOGY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'TOKYO UNIVERSITY OF MARINE SCIENCE AND TECHNOLOG.+',
                                                                'TOKYO UNIVERSITY OF MARINE SCIENCE AND TECHNOLOGY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL UNIVERSITY CORPORATION TOKYO UNIVERSITY OF MARINE SCIENCE AND TECHNOLOGY,KUROISHI INC',
                                                                'TOKYO UNIVERSITY OF MARINE SCIENCE AND TECHNOLOGY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL UNIVERSITY CORPORATION, TOKYO UNIVERSITY OF MARINE SCIENCE AND TECHNOLOGY',
                                                                'TOKYO UNIVERSITY OF MARINE SCIENCE AND TECHNOLOGY', regex=True)
        
        #CJ CHEILJEDANG CORPORATION
        pandas_df['company'] = pandas_df['company'].str.replace(r'CJ CHEILJEDAN.+',
                                                                'CJ CHEILJEDANG CORP', regex=True)
        #KAO CORPORATION
        pandas_df['company'] = pandas_df['company'].str.replace(r'KAO CORPORATIO.+',
                                                                'KAO CORPORATION', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'KAO COOPORATION',
                                                                'KAO CORPORATION', regex=True)
        
        
        #SEKISUI CHEMICAL
        pandas_df['company'] = pandas_df['company'].str.replace(r'SEKISUI CHEMICA.+',
                                                                'SEKISUI CHEMICAL', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SEKISUI CHEM CO LTD, TOYOBO CO LTD',
                                                                'SEKISUI CHEMICAL', regex=True)
        
        #CHISSO CORPORATION
        pandas_df['company'] = pandas_df['company'].str.replace(r'CHISSO CORPORATIO.+',
                                                                'CHISSO CORPORATION', regex=True)

        #OSAKA UNIVERSITY
        pandas_df['company'] = pandas_df['company'].str.replace(r'OSAKA UNIVERSIT.+',
                                                                'OSAKA UNIVERSITY', regex=True)
        
        #ABBOTT LABORATORIES
        pandas_df['company'] = pandas_df['company'].str.replace(r'ABBOT.+',
                                                                'ABBOTT LABORATORIES', regex=True)
        
        #IUCF-HYU (INDUSTRY-UNIVERSITY COOPERATION FOUNDATION HANYANG UNIVERSITY)
        pandas_df['company'] = pandas_df['company'].str.replace(r'IUCF-HY.+',
                                                                'IUCF-HYU', regex=True)
        
        
        #MICHIHIKO KOBAYASHI,MICHIHIKO KOBAYASHI,TOYOBO CO LTD
        pandas_df['company'] = pandas_df['company'].str.replace(r'MICHIHIKO KOBAYASH.+',
                                                                'MICHIHIKO KOBAYASHI', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'MICHIHIKO KOBAYASHI,TOYOBO CO LTD', 'MICHIHIKO KOBAYASHI', regex=True)
        
        
        #EVOGENE LTD [IL]
        pandas_df['company'] = pandas_df['company'].str.replace(r'EVOGENE LTD [IL]', 'EVOGENE LTD', regex=True)
        
        #NSERC
        pandas_df['company'] = pandas_df['company'].str.replace(r'CANADA NAT RES COUNCIL [CA]', 'NSERC', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL RESEARCH COUNCIL OF CANAD.+', 'NSERC', regex=True)
        
        #GSK
        pandas_df['company'] = pandas_df['company'].str.replace(r'HUMAN GENOME SCIENCES IN.+', 'GSK', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'GSK.+', 'GSK', regex=True)
        
        #SERES
        pandas_df['company'] = pandas_df['company'].str.replace(r'SERES HEALTH INC', 'SERES', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SERES THERAPEUTICS, INC', 'SERES', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SERES.+',
                                                                'SERES', regex=True)
        
        #MISTUBISHI
        pandas_df['company'] = pandas_df['company'].str.replace(r'API CORPORATION',
                                                                'MITSUBISHI', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'MITSUBISHI CH.+',
                                                                'MITSUBISHI', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'NIHON SHOKUHIN KAKO CO LTDHOKKAIDO UNIVERSITY',
                                                                'MITSUBISHI', regex=True)
        
        #NATIONAL INSTITUTE OF TECHNOLOGY AND EVALUATION,WASEDA UNIVERSITY, CHISSO CORPORATION
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL INSTITUTE OF TECHNOLOGY AND EVALUATIO.+',
                                                                'NATIONAL INSTITUTE OF TECHNOLOGY AND EVALUATION', regex=True)
        
        #NUFARM
        pandas_df['company'] = pandas_df['company'].str.replace(r'NUSEE.+',
                                                                'NUFARM', regex=True)
        
        #CORTEVA
        pandas_df['company'] = pandas_df['company'].str.replace(r'PIONEER H.+',
                                                                'CORTEVA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'DOW AGROSCIENC.+',
                                                                'CORTEVA', regex=True)
        
        #SANOFI
        pandas_df['company'] = pandas_df['company'].str.replace(r'AVENTIS.+',
                                                                'SANOFI', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SANOFI.+',
                                                                'SANOFI', regex=True)
        
        #CATALYST BIOSCIENCES INC
        pandas_df['company'] = pandas_df['company'].str.replace(r'CATALYST BIOSCIENCE.+',
                                                                'CATALYST BIOSCIENCES', regex=True)
        
        #CELANESE CORP
        pandas_df['company'] = pandas_df['company'].str.replace(r'NUTRINOVA NUTRITIO.+',
                                                                'CELANESE CORPORATION', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'NUTRINOVA NUTRITI ON SPECIALTIES & FOOD INGREDIENTS GMBH \(DE', 'CELANESE CORPORATION', regex=True)
        
        #MATRIX GENETICS
        pandas_df['company'] = pandas_df['company'].str.replace(r'MATRIX GENETIC.+',
                                                                'MATRIX GENETICS', regex=True)
        
        #EXXONMOBIl
        pandas_df['company'] = pandas_df['company'].str.replace(r'EXXONMOBI.+',
                                                                'EXXONMOBIL', regex=True)
        
        #INRES
        pandas_df['company'] = pandas_df['company'].str.replace(r'CROP FUNCTIONAL GENOMICS CENTE.+',
                                                                'INRES', regex=True)
        
        #CHR HANSEN
        pandas_df['company'] = pandas_df['company'].str.replace(r'JENNEWEIN BIOTECHNOLOGIE GMB.+',
                                                                'CHR HANSEN', regex=True)
        
        #THE UNIVERSITY COURT OF THE UNIVERSITY OF ABERDEEN
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE UNIVERSITY COURT OF THE UNIVERSITY OF ABERDEE.+',
                                                                'UNIVERSITY OF ABERDEEN', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV ABERDEE.+',
                                                                'UNIVERSITY OF ABERDEEN', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIVERSITY OF ABERDEE.+',
                                                                'UNIVERSITY OF ABERDEEN', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'ABERDEEN UNIVERSIT.+',
                                                                'UNIVERSITY OF ABERDEEN', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE UNIV COURT OF THE UNIV OF ABERDEEN [GB]',
                                                                'UNIVERSITY OF ABERDEEN', regex=True)
        
        
        #NISSUI
        pandas_df['company'] = pandas_df['company'].str.replace(r'NISSUI.+',
                                                                'NISSUI', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'NIPPON SUISAN KAISH.+',
                                                                'NISSUI', regex=True)
        
        #SAREPTA
        pandas_df['company'] = pandas_df['company'].str.replace(r'AVI BIOPHARMA.+',
                                                                'SAREPTA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SAREPTA.+',
                                                                'SAREPTA', regex=True)
        
        #TOYOTA
        pandas_df['company'] = pandas_df['company'].str.replace(r'TOYOTA.+',
                                                                'TOYOTA', regex=True)
        
        #KANEKA CORP
        pandas_df['company'] = pandas_df['company'].str.replace(r'KANEKA COR.+',
                                                                'KANEKA CORP', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'EUROGENTE.+',
                                                                'KANEKA CORP', regex=True)
        
        
        #ALL
        #AXCELLA
        pandas_df['company'] = pandas_df['company'].str.replace(r'PRONUTRIA IN.+',
                                                                'AXCELLA', regex=True)
        
        #UNI OF WASHINGTON
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIVERSITY OF WASHINGTO.+',
                                                                'UNIVERSITY OF WASHINGTON', regex=True)
        
        #LUIS BERNHARD
        pandas_df['company'] = pandas_df['company'].str.replace(r'LUIS BERNHAR.+',
                                                                'LUIS BERNHARD', regex=True)        
        
        
        #SUNTORY LTD
        pandas_df['company'] = pandas_df['company'].str.replace(r'SUNTOR.+',
                                                                'SUNTORY LTD', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'FLORIGENE LIMITEDTHE UNIVERSITY OF QUEENSLAND',
                                                                'SUNTORY LTD', regex=True)
        
        #NAGOYA UNI
        pandas_df['company'] = pandas_df['company'].str.replace(r'PRESIDENT OF NAGOYA UNIVERSITY',
                                                                'NAGOYA UNIVERSITY', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'NAGOYA UNIVERSIT.+',
                                                                'NAGOYA UNIVERSITY', regex=True)
        #BIOTEC ASA
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIOTEC AS.+',
                                                                'BIOTEC ASA', regex=True)
        
        #GELTOR
        pandas_df['company'] = pandas_df['company'].str.replace(r'GELTOR.+',
                                                                'GELTOR', regex=True)
        
        #SAMSUNG ELECTRONICS
        pandas_df['company'] = pandas_df['company'].str.replace(r'SAMSUNG ELECTRONIC.+',
                                                                'SAMSUNG ELECTRONICS', regex=True)
        
        #BIORIGINAL FOOD & SCIENCE CORP. (CA)
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIORIGINAL FOOD & SCIENCE CORP. (CA)',
                                                                'BIORIGINAL FOOD AND SCIENCE CORPORATION', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIORIGINAL FOOD AND SCIENCE CORP.+',
                                                                'BIORIGINAL FOOD AND SCIENCE CORPORATION', regex=True)
        
        #HEALTH PROTECTION AGENCY
        pandas_df['company'] = pandas_df['company'].str.replace(r'HEALTH PROTECTION AGENC.+',
                                                                'HEALTH PROTECTION AGENCY', regex=True)
                                                                
        #GREEN PHENOL
        pandas_df['company'] = pandas_df['company'].str.replace(r'GREEN PHENO.+',
                                                                'GREEN PHENOL DEVELOPMENT', regex=True)
                                                                
        #SBI BIOTECH CO
        pandas_df['company'] = pandas_df['company'].str.replace(r'SBI BIOTECH CO.+',
                                                                'SBI BIOTECH CO', regex=True)
        
        #TECHNION RES
        pandas_df['company'] = pandas_df['company'].str.replace(r'TECHNION RES.+',
                                                                'TECHNION RESEARCH', regex=True)    
        
        #MICROCOAT BIOTECHNOLOGIE
        pandas_df['company'] = pandas_df['company'].str.replace(r'MICROCOAT BIOTECH.+',
                                                                'MICROCOAT', regex=True)
        
        #ROQUETTE
        pandas_df['company'] = pandas_df['company'].str.replace(r'ROQUETTE.+',
                                                                'ROQUETTE FRERES', regex=True)
        
        #EBARA CORPORATION
        pandas_df['company'] = pandas_df['company'].str.replace(r'EBARA CORPORATIO.+',
                                                                'EBARA CORPORATION', regex=True)
        
        #NISSHINBO INDUSTRIES
        pandas_df['company'] = pandas_df['company'].str.replace(r'NISSHINBO INDUSTRIE.+',
                                                                'NISSHINBO INDUSTRIES', regex=True)
        #FUJITA ACADEMY
        pandas_df['company'] = pandas_df['company'].str.replace(r'FUJITA ACAD.+',
                                                                'FUJITA ACADEMY', regex=True)
        
        #KYOWA HAKKO
        pandas_df['company'] = pandas_df['company'].str.replace(r'KYOWA HAKK.+',
                                                                'KYOWA HAKKO', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'KYOWA CONCRETE INDUSTRY CO LTD',
                                                                'KYOWA HAKKO', regex=True)
        
        #EVOGENE
        pandas_df['company'] = pandas_df['company'].str.replace(r'EVOGEN.+',
                                                                'EVOGENE', regex=True)
        
        #KIEPPE PATRIMONIAL
        pandas_df['company'] = pandas_df['company'].str.replace(r'BRASKEM.+',
                                                                'BRASKEM', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'BRASKEM',
                                                                'KIEPPE PATRIMONIAL', regex=True)

        
        #IFREMER
        pandas_df['company'] = pandas_df['company'].str.replace(r'IFREME.+',
                                                                'IFREMER', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'IFREMER',
                                                                'GOVERNMENT OF FRANCE', regex=True)
        
        #COMMISSARIAT ENERGIE ATOMIQUE
        pandas_df['company'] = pandas_df['company'].str.replace(r'COMMISSARIAT ENERGIE ATOMIQU.+',
                                                                'COMMISSARIAT ENERGIE ATOMIQUE', regex=True)
        
        #BONUMOSE
        pandas_df['company'] = pandas_df['company'].str.replace(r'BONUMOS.+',
                                                                'BONUMOSE', regex=True)
        
        #TERACLON
        pandas_df['company'] = pandas_df['company'].str.replace(r'TERACLO.+',
                                                                'TERACLON', regex=True)
        
        #APPLIED BIOSYSTEMS
        pandas_df['company'] = pandas_df['company'].str.replace(r'APPLIED BIOSYSTEM.+',
                                                                'APPLIED BIOSYSTEMS', regex=True)
        
        #PFIZER INC
        pandas_df['company'] = pandas_df['company'].str.replace(r'PFIZE.+',
                                                                'PFIZER', regex=True)
        
        #INSTITUT NATIONAL DE LA RECHERCHE AGRONOMIQUE
        pandas_df['company'] = pandas_df['company'].str.replace(r'INSTITUT NATIONAL DE LA RECHERCHE AGRONOMIQU.+',
                                                                'AGRONOMIQUE INST', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'AGRONOMIQUE INS.+',
                                                                'AGRONOMIQUE INST', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'AGRONOMIQUE INST',
                                                                'INRA', regex=True)
        
        #PLASMIA BIOTECH
        pandas_df['company'] = pandas_df['company'].str.replace(r'INSTITUT NATIONAL DE LA RECHERCHE AGRONOMIQU.+',
                                                                'AGRONOMIQUE INST', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'PLASMIA BIOTEC.+',
                                                                'PLASMIA BIOTECH', regex=True)
        
        #ARCTICZYMES
        pandas_df['company'] = pandas_df['company'].str.replace(r'ARCTICZYME.+',
                                                                'ARCTICZYMES', regex=True)
        
        #RIGEL PHARMACEUTICALS
        pandas_df['company'] = pandas_df['company'].str.replace(r'RIGEL PHARMACEUTICAL.+',
                                                                'RIGEL PHARMACEUTICALS', regex=True)
        
        #KENJI KANGAWA
        pandas_df['company'] = pandas_df['company'].str.replace(r'KENJI KANGAW.+',
                                                                'KENJI KANGAWA', regex=True)
        
        #THE SECRETARY OF STATE FOR DEFENCE
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE SECRETARY OF STATE FOR DEFENC.+',
                                                                'THE SECRETARY OF STATE FOR DEFENCE', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'PIONEER HI BRED IN.+',
                                                                'PIONEER HI BRED INT', regex=True)
        #NOVARTIS
        pandas_df['company'] = pandas_df['company'].str.replace(r'NOVARTI.+',
                                                                'NOVARTIS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'LEK PHARMACEUTICALS',
                                                                'NOVARTIS', regex=True)
        
        
        #THE TRUSTEES OF PRINCETON UNIVERSITY
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE TRUSTEES OF PRINCETON UNIVERSIT.+',
                                                                'THE TRUSTEES OF PRINCETON UNIVERSITY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'PRINCETON UNIVERSIT.+',
                                                                'PRINCETON UNIVERSITY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE TRUSTEES OF PRINCETON UNIVERSITY',
                                                                'PRINCETON UNIVERSITY', regex=True)
       
        
        #LEK PHARMACEUTICALS
        pandas_df['company'] = pandas_df['company'].str.replace(r'LEK PHARMACEUTICAL.+',
                                                                'LEK PHARMACEUTICALS', regex=True)
        
        #GOLDSCHMIDT
        pandas_df['company'] = pandas_df['company'].str.replace(r'GOLDSCHMID.+',
                                                                'GOLDSCHMIDT', regex=True)
        
        #VNV NEWCO
        pandas_df['company'] = pandas_df['company'].str.replace(r'VNV NEWC.+',
                                                                'VNV NEWCO', regex=True)
        
        #YALE UNIVERSITY
        pandas_df['company'] = pandas_df['company'].str.replace(r'YALE UNIVERSIT.+',
                                                                'YALE UNIVERSITY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV YAL.+',
                                                                'YALE UNIVERSITY', regex=True)
        
        
        #CENTRUM VOOR PLANTENVEREDELINGS
        pandas_df['company'] = pandas_df['company'].str.replace(r'CENTRUM VOOR PLANTENVEREDELING.+',
                                                                'CENTRUM VOOR PLANTENVEREDELINGS', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'CT VOOR PLANTENVEREDELING.+',
                                                                'CENTRUM VOOR PLANTENVEREDELINGS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'CENTRUM VOOR PLANTENVEREDELINGS',
                                                                'WAGENINGEN UNIVERSOTY', regex=True)
        
        #ANTIBODY AG 4
        pandas_df['company'] = pandas_df['company'].str.replace(r'ANTIBODY AG 4.+',
                                                                'ANTIBODY AG 4', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'ANTIBODY AG 4.+',
                                                                'AGENUS', regex=True)
        
        #INVITROGEN
        pandas_df['company'] = pandas_df['company'].str.replace(r'INVITROGEN.+',
                                                                'INVITROGEN', regex=True)
        
        #AVESTHA
        pandas_df['company'] = pandas_df['company'].str.replace(r'AVESTHA.+',
                                                                'AVESTHA GEN', regex=True)
        
        #ISHIKAWA PREFECTURE
        pandas_df['company'] = pandas_df['company'].str.replace(r'ISHIKAWA PREFECTUR.+',
                                                                'ISHIKAWA PREFECTURE', regex=True)
        
        #MICHIGAN STATE
        pandas_df['company'] = pandas_df['company'].str.replace(r'MICHIGAN STAT.+',
                                                                'MICHIGAN STATE UNIVERSITY', regex=True)
        
        #INSTITUT PASTEUR
        pandas_df['company'] = pandas_df['company'].str.replace(r'INSTITUT PASTEU.+',
                                                                'INSTITUT PASTEUR', regex=True)
        
        #INSERM
        pandas_df['company'] = pandas_df['company'].str.replace(r'INSTITUT NATIONAL DE LA SANT.+',
                                                                'INSERM', regex=True)
        
        #ILLUMINA CAMBRIDGE LTD [GB]
        pandas_df['company'] = pandas_df['company'].str.replace(r'SOLEXA',
                                                                'ILLUMINA CAMBRIDGE LTD [GB]', regex=True)
        
        #KANSAI DENRYOKU
        pandas_df['company'] = pandas_df['company'].str.replace(r'KANSAI DENRYOK.+',
                                                                'KANSAI DENRYOKU', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'KANSAI DENRYOKU',
                                                                'KANSAI ELECTRIC POWER CO INC:THE', regex=True)
        
        
        #APPLIED MOLECULAR TRANSP
        pandas_df['company'] = pandas_df['company'].str.replace(r'APPLIED MOLECULAR TRANS.+',
                                                                'APPLIED MOLECULAR TRANSPORT', regex=True)
        
        
        #ACTIVE BIOTECH AB
        pandas_df['company'] = pandas_df['company'].str.replace(r'ACTIVE BIOTECH A.+',
                                                                'ACTIVE BIOTECH AB', regex=True)
        
        #LOMA LINDA UNIVERSITY
        pandas_df['company'] = pandas_df['company'].str.replace(r'LOMA LINDA UNIVERSIT.+',
                                                                'LOMA LINDA UNIVERSITY', regex=True)
        
        #SCHWARZ WOLFGANG
        pandas_df['company'] = pandas_df['company'].str.replace(r'SCHWARZ WOLFGAN.+',
                                                                'SCHWARZ WOLFGANG', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'WOLFGANG H SCHWARZ',
                                                                'SCHWARZ WOLFGANG', regex=True)
        
        #TORAY
        pandas_df['company'] = pandas_df['company'].str.replace(r'TORAY .+',
                                                                'TORAY', regex=True)
        
        #NEW ENGLAND BIOLABS
        pandas_df['company'] = pandas_df['company'].str.replace(r'NEW ENGLAND BIOLAB.+',
                                                                'NEW ENGLAND BIOLABS', regex=True)
        
        #NAIST
        pandas_df['company'] = pandas_df['company'].str.replace(r'NARA INSTITUTE OF SCIENCE AN.+',
                                                                'NAIST', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'PRESIDENT OF NARA INSTITUTE OF SCIENCE AND TECHNOLOGY',
                                                                'NAIST', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL UNIVERSITY CORPORATION NARA.+',
                                                                'NAIST', regex=True)
        
        #FORSCHUNGSZENTRUM JUELICH
        pandas_df['company'] = pandas_df['company'].str.replace(r'FORSCHUNGSZENTRUM JUELIC.+',
                                                                'FORSCHUNGSZENTRUM JUELICH', regex=True)
       
        #PF MEDICAMENT
        pandas_df['company'] = pandas_df['company'].str.replace(r'PF MEDICAMEN.+',
                                                                'PIERRE FABRE MEDICAMENT', regex=True)
        
        #UNIVERSITEIT GENT
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIVERSITEIT GEN.+',
                                                                'UNIVERSITEIT GENT', regex=True)
        
        #SAFEWHITE
        pandas_df['company'] = pandas_df['company'].str.replace(r'SAFEWHIT.+',
                                                                'SAFEWHITE', regex=True)
        
        #TOKYO INSTITUTE OF TECHNOLOGY
        pandas_df['company'] = pandas_df['company'].str.replace(r'TOKYO INSTITUTE OF TECHNOLOG.+',
                                                                'TOKYO INSTITUTE OF TECHNOLOGY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'TOKYO INST TEC.+',
                                                                'TOKYO INSTITUTE OF TECHNOLOGY', regex=True)
        
        #JOHANNES GUTENBERG-UNIVERSITAET MAINZ
        pandas_df['company'] = pandas_df['company'].str.replace(r'JOHANNES GUTENBERG-UNIVERSITAET MAIN.+',
                                                                'JOHANNES GUTENBERG-UNIVERSITAET MAINZ', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'JOHANNES GUTENBERG UNIVERSITAET MAINZ',
                                                                'JOHANNES GUTENBERG-UNIVERSITAET MAINZ', regex=True)
        
        #SOLEXA
        pandas_df['company'] = pandas_df['company'].str.replace(r'SOLEXA .+',
                                                                'SOLEXA', regex=True)
        
        #TOTAL
        pandas_df['company'] = pandas_df['company'].str.replace(r'TOTAL .+',
                                                                'TOTAL', regex=True)
        
        #INST UNIV DE CIENCIA
        pandas_df['company'] = pandas_df['company'].str.replace(r'INST UNIV DE CIENCI.+',
                                                                'INST UNIV DE CIENCIA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'INSTITUT UNIV DE CIENCI.+',
                                                                'INST UNIV DE CIENCIA', regex=True)
        #GLYCOBIA INC
        pandas_df['company'] = pandas_df['company'].str.replace(r'GLYCOBIA IN.+',
                                                                'GLYCOBIA INC', regex=True)
        #ETH ZURICH
        pandas_df['company'] = pandas_df['company'].str.replace(r'ETH ZURIC.+',
                                                                'ETH ZURICH', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'ETH ZUERICH [CH]',
                                                                'ETH ZURICH', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'ETH ZUERICH [CH]',
                                                                'ETH ZURICH', regex=True)
        
        
        #NIPRO CORP
        pandas_df['company'] = pandas_df['company'].str.replace(r'NIPRO COR.+',
                                                                'NIPRO CORP', regex=True)
        
        #PIONEER HI-BRED
        pandas_df['company'] = pandas_df['company'].str.replace(r'PIONEER HI-BRE.+',
                                                                'PIONEER HI-BRED', regex=True)
        
        #MITOKOR
        pandas_df['company'] = pandas_df['company'].str.replace(r'MITOKO.+',
                                                                'MITOKOR', regex=True)
        
        #AMYRIS
        pandas_df['company'] = pandas_df['company'].str.replace(r'AMYRI.+',
                                                                'AMYRIS', regex=True)
        
        #CHRISTIAN PETZELT
        pandas_df['company'] = pandas_df['company'].str.replace(r'PETZELT.+',
                                                                'CHRISTIAN PETZELT', regex=True)
        #INSTITUTO BIOMAR
        pandas_df['company'] = pandas_df['company'].str.replace(r'INSTITUTO BIOMA.+',
                                                                'INSTITUTO BIOMAR', regex=True)
        
        #CENTRO DE INGENIERIA GENETICA
        pandas_df['company'] = pandas_df['company'].str.replace(r'CENTRO DE INGENIERIA GENETIC.+',
                                                                'CENTRO DE INGENIERIA GENETICA', regex=True)
        
        #INTREXON
        pandas_df['company'] = pandas_df['company'].str.replace(r'INTREXON CORPORATIO.+',
                                                                'PRECIGEN', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'INTREXON CORP [US]',
                                                                'PRECIGEN', regex=True)
        
        #MELT&MARBLE
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIOPETROLIA AB [SE]',
                                                                'MELT&MARBLE', regex=True)
        
        #KOREA OCEAN RESEARCH AND DEVELOPMENT
        pandas_df['company'] = pandas_df['company'].str.replace(r'KOREA OCEAN RESEARCH AND DEVELOPMEN.+',
                                                                'KIOST', regex=True)
        #IDEMITSU KOSAN
        pandas_df['company'] = pandas_df['company'].str.replace(r'IDEMITSU KOSA.+',
                                                                'IDEMITSU KOSAN', regex=True)
        #KOBE UNIVERSITY
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL UNIVERSITY CORPORATION KOBE UNIVE.+',
                                                                'KOBE UNIVERSITY', regex=True)
        
        #NATIONAL RESEARCH COUNCIL CANADA
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL RESEARCH COUNCIL CANAD.+',
                                                                'NATIONAL RESEARCH COUNCIL CANADA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'CANADA NAT RES COUNCI.+',
                                                                'NATIONAL RESEARCH COUNCIL CANADA', regex=True)
        
        #TOKIO INSTITUTE OF TECHNOLOGY
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL UNIVERSITY CORPORATION TOKYO INSTITUTE OF TECHNOLOGY','TOKIO INSTITUTE OF TECHNOLOGY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV TOKYO NAT UNIV CORP [JP]','TOKIO INSTITUTE OF TECHNOLOGY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'TOKYO INSTITUTE OF TECHNOLOGY','TOKIO INSTITUTE OF TECHNOLOGY', regex=True)
        
        #OTSUKA PHARMACEUTICAL
        pandas_df['company'] = pandas_df['company'].str.replace(r'OTSUKA PHA.+','OTSUKA PHARMACEUTICAL', regex=True)
        
        #NUFARM
        pandas_df['company'] = pandas_df['company'].str.replace(r'NUFAR.+','NUFARM', regex=True)
        
        #GLYCOBIA
        pandas_df['company'] = pandas_df['company'].str.replace(r'GLYCOBI.+','GLYCOBIA', regex=True)
        
        #NATIONAL INSTITUTE OF AGROBIOLOGICAL SCIENCES
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL INSTITUTE OF AGROBIOLOGI.+','NIAS', regex=True)
        
        #LONZA
        pandas_df['company'] = pandas_df['company'].str.replace(r'LONZ.+','LONZA', regex=True)
        
        #GLYCOBIA
        pandas_df['company'] = pandas_df['company'].str.replace(r'GLYCOBI.+','GLYCOBIA', regex=True)
        
        #MERCK
        pandas_df['company'] = pandas_df['company'].str.replace(r'GLYCOFI INC. (US)','MERCK', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'MERCK AND CO INC','MERCK', regex=True)
        
        #IRONWOOD PHARMACEUTICALS
        pandas_df['company'] = pandas_df['company'].str.replace(r'MICROBIA INC','IRONWOOD PHARMACEUTICALS', regex=True)
        
        #EZAKI GLICO
        pandas_df['company'] = pandas_df['company'].str.replace(r'EZAKI GLIC.+','EZAKI GLICO', regex=True)
        
        #FARMHANNONG
        pandas_df['company'] = pandas_df['company'].str.replace(r'FARMHANNON.+','FARMHANNONG', regex=True)
        
        #ROTHAMSTED RESEARCH LIMITED
        pandas_df['company'] = pandas_df['company'].str.replace(r'ROTHAMSTE.+','ROTHAMSTED', regex=True)
        
        #JOULE
        pandas_df['company'] = pandas_df['company'].str.replace(r'JOUL.+','JOULE UNLIMITED', regex=True)
        
        #LUDWIG-MAXIMILIANS-UNIVERSITAT
        pandas_df['company'] = pandas_df['company'].str.replace(r'LUDWIG-MAXIMILIAN.+','LUDWIG-MAXIMILIANS-UNIVERSITAT', regex=True)
        
        #VERTEX PHARMACEUTICALS
        pandas_df['company'] = pandas_df['company'].str.replace(r'VERTEX PHARMACEUTICA.+','VERTEX PHARMACEUTICALS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'AURORA BIOSCIENCES CORPORATION (US)','VERTEX PHARMACEUTICALS', regex=True)
        
        #UTILIZATION OF CARBON DIOXIDE INSTITUTE
        pandas_df['company'] = pandas_df['company'].str.replace(r'UTILIZATION OF CARBON DIOXIDE INS.+','UTILIZATION OF CARBON DIOXIDE INSTITUTE', regex=True)
        
        #UNIVERSITY OF TSUKU
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIVERSITY OF TSU.+','UNIVERSITY OF TSUKUBA', regex=True)
        
        #UNIVERSITY OF BRISTO
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIVERSITY OF BRISTO.+','UNIVERSITY OF BRISTOL', regex=True)
        
        #UNIVERSITY OF TROMSO (NO)
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIVERSITY OF TROMSO (NO)','UNIVERSITY OF TROMSO', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV TROMSOE[NO]','UNIVERSITY OF TROMSO', regex=True)
        
        #UNIV SHEFFIELD
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV SHEFFIEL.+','UNIVERSITY SHEFFIELD', regex=True)
        
        #UNIV NANYANG TEC
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV NANYANG TEC.+','UNIV NANYANG TECH [SG]', regex=True)
        
        #UNIV NANJIN
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV NANJINGA [CN]','UNIV NANYANG TECH', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV NANJING [CN]','UNIV NANYANG TECH', regex=True)
        
        #UNILEVER
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNILEVE.+','UNILEVER', regex=True)
        
        #TAKEDA CHEMICAL INDUSTRIES LTD
        pandas_df['company'] = pandas_df['company'].str.replace(r'SHIRE HUMAN GENETIC THERAPIES INC','TAKEDA CHEMICAL INDUSTRIES LTD', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'TRANSKARYOTIC THERAPI.+','TAKEDA CHEMICAL INDUSTRIES LTD', regex=True)
        
        #TOYOBO CO LTD
        pandas_df['company'] = pandas_df['company'].str.replace(r'TOYO BOSEK.+','TOYOBO CO LTD', regex=True)
        
        #TOSOH CORP
        pandas_df['company'] = pandas_df['company'].str.replace(r'TOSOH COR.+','TOSOH CORPORATION', regex=True)
        
        #THIRY, MICHE
        pandas_df['company'] = pandas_df['company'].str.replace(r'THIRY, MICHE.+','THIRY, MICHEL', regex=True)
        
        #THERMOSTABLE ENZYME LABORATORY
        pandas_df['company'] = pandas_df['company'].str.replace(r'THERMOSTABLE ENZYME LABORATOR.+',
                                                                'THERMOSTABLE ENZYME LABORATORY', regex=True)
        
        #THE UNIVERSITY OF TOKY
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE UNIVERSITY OF TOKY.+',
                                                                'TOKYO UNIVERSITY', regex=True)
        
        #THE UNIVERSITY OF MARYLAND AT BALTIMORE (US)
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV MARYLAND BIOTECH INST [US]',
                                                                'UNIVERSITY OF MARYLAND', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE UNIVERSITY OF MARYLAND AT BALTIMORE (US)',
                                                                'UNIVERSITY OF MARYLAND', regex=True)
        
        #THE UNIVERSITY OF CHICAG
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE UNIVERSITY OF CHICAG.+',
                                                                'THE UNIVERSITY OF CHICAGO', regex=True)
        
        #THE JOHNS HOPKINS UNIVERSITY
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE JOHNS HOPKINS UNIVERSITY',
                                                                'JOHNS HOPKINS UNIVERSITY', regex=True)
        
        #KYOTO UNIVERSITY
        pandas_df['company'] = pandas_df['company'].str.replace(r'KYOTO UNIVERSIT.+',
                                                                'KYOTO UNIVERSITY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE HEAD OF KYOTO UNIVERSITY',
                                                                'KYOTO UNIVERSITY', regex=True)
        
        #THE BROAD INSTITUTE
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE BROAD INSTITUT.+',
                                                                'THE BROAD INSTITUTE', regex=True)
        
        #TEL HASHOMER MEDICAL RESEARCH
        pandas_df['company'] = pandas_df['company'].str.replace(r'TEL HASHOMER MEDICAL RES INFRA [IL]',
                                                                'TEL HASHOMER MEDICAL RESEARCH INFRASTRUCTURE AND SERVICES LTD. (IL)', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'TEL HASHOMER MEDICAL RESEARCH INFRASTRUCTURE AND SERVICES LTD. (IL)',
                                                                'TEL HASHOMER MEDICAL RESEARCH', regex=True)
        
        #MUNICH UNIVER
        pandas_df['company'] = pandas_df['company'].str.replace(r'TECHNISCHE UNIVERSITAET MUENC.+',
                                                                'TECHNICAL UNIVERSITY OF MUNICH', regex=True)
        #TARGETED GROWTH
        pandas_df['company'] = pandas_df['company'].str.replace(r'TARGETED GROWT.+',
                                                                'TARGETED GROWTH', regex=True)
        
        #SYNGULON
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV LELAND STANFORD JUNIOR [US]',
                                                                'STANFORD UNIVERSITY', regex=True)
        
        #SYNGULON
        pandas_df['company'] = pandas_df['company'].str.replace(r'SYNGULO.+',
                                                                'SYNGULON', regex=True)
        
        #STEPHEN R HAMILT
        pandas_df['company'] = pandas_df['company'].str.replace(r'STEPHEN R HAMILT.+',
                                                                'STEPHEN R HAMILTON', regex=True)
        
        #SOGANG UNIVERSITY RES
        pandas_df['company'] = pandas_df['company'].str.replace(r'SOGANG UNIVERSITY RES.+',
                                                                'SOGANG UNIVERSITY RESEARCH', regex=True)
        
        #SNU R&DB FOUNDATION
        pandas_df['company'] = pandas_df['company'].str.replace(r'SNU R&DB FOUNDATIO.+',
                                                                'SNU R&DB FOUNDATION', regex=True)
        
        #SEOUL NATIONAL UNIVERSIT
        pandas_df['company'] = pandas_df['company'].str.replace(r'SEOUL NATIONAL UNIVERSIT.+',
                                                                'SEOUL NATIONAL UNIVERSITY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'SNU R&DB FOUNDATION',
                                                                'SEOUL NATIONAL UNIVERSITY', regex=True)
        
        #ROCHE DIAGNOSTIC
        pandas_df['company'] = pandas_df['company'].str.replace(r'ROCHE DIAGNOSTIC.+',
                                                                'ROCHE DIAGNOSTICS', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'F HOFFMANN-LA ROCHE AG',
                                                                'ROCHE DIAGNOSTICS', regex=True)
        
        #RESEARCH INSTITUTE OF INNOVATIVE TECHNOLOGY FOR THE EART
        pandas_df['company'] = pandas_df['company'].str.replace(r'RESEARCH INSTITUTE OF INNOVATIVE TECHNOLOGY FOR THE EART.+',
                                                                'RESEARCH INSTITUTE OF INNOVATIVE TECHNOLOGY FOR THE EARTH', regex=True)
        
        #RADIOMETER MEDICAL APS
        pandas_df['company'] = pandas_df['company'].str.replace(r'RADIOMETER MEDICAL AP.+',
                                                                'RADIOMETER MEDICAL APS', regex=True)
        
        #PURATO
        pandas_df['company'] = pandas_df['company'].str.replace(r'PURATO.+',
                                                                'PURATOS', regex=True)
        
        #PURAC BIOCHEM - CORBION
        pandas_df['company'] = pandas_df['company'].str.replace(r'PURAC BIOCHE.+',
                                                                'PURAC BIOCHEM', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'PURAC BIOCHEM',
                                                                'CORBION', regex=True)
        
        #PROVIVI INC
        pandas_df['company'] = pandas_df['company'].str.replace(r'PROVIVI IN.+',
                                                                'PROVIVI INC', regex=True)
        
        #PROTERRO
        pandas_df['company'] = pandas_df['company'].str.replace(r'PROTERR.+',
                                                                'PROTERRO INC', regex=True)
        
        #PROLUME
        pandas_df['company'] = pandas_df['company'].str.replace(r'PROLUM.+',
                                                                'PROLUME LTD', regex=True)
        
        #POSCO
        pandas_df['company'] = pandas_df['company'].str.replace(r'POSC.+',
                                                                'POSCO', regex=True)
        
        #OZEKI CORPORATIO
        pandas_df['company'] = pandas_df['company'].str.replace(r'OZEKI CORPORATIO.+',
                                                                'OZEKI CORPORATION', regex=True)
        
        #OXITEC LT
        pandas_df['company'] = pandas_df['company'].str.replace(r'OXITEC LT.+',
                                                                'OXITEC LTD', regex=True)
        
        #OKAZAKI
        pandas_df['company'] = pandas_df['company'].str.replace(r'OKAZAKI NATIONAL RESEARCH INSTI.+',
                                                                'OKAZAKI NATIONAL RESEARCH INSTITUTES', regex=True)
        
        #NSGENE A
        pandas_df['company'] = pandas_df['company'].str.replace(r'NSGENE A.+',
                                                                'NSGENE A/S', regex=True)
        
        #NORWEGIAN SCHOOL OF VETERINARY SCIEN
        pandas_df['company'] = pandas_df['company'].str.replace(r'NORWEGIAN SCHOOL OF VETERINARY SCIEN.+',
                                                                'NORWEGIAN SCHOOL OF VETERINARY SCIENCE', regex=True)
        
        #NISHIKAWA RUBBER
        pandas_df['company'] = pandas_df['company'].str.replace(r'NISHIKAWA RUBBE.+',
                                                                'NISHIKAWA RUBBER', regex=True)
        
        #NIIGATA UNIVERSI
        pandas_df['company'] = pandas_df['company'].str.replace(r'NIIGATA UNIVERSI.+',
                                                                'NIIGATA UNIVERSITY', regex=True)
        
        #NEC SOFTWARE LTD [JP]
        pandas_df['company'] = pandas_df['company'].str.replace(r'NEC SOFTWARE LTD [JP]',
                                                                'NEC SOFT CORPORATION', regex=True)
        
        #NATIONAL UNIVERSITY CORPORATION KYUSHU UNIVERSIT
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'KYUSHU UNIVERSIT.+',
                                                                'KYUSHU UNIVERSITY', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'NATIONAL UNIVERSITY CORPORATION KYUSHU UNIVERSIT.+',
                                                                'KYUSHU UNIVERSITY', regex=True)
        
        
        #NAGOYA INSTITUTE OF TECHNOLOGY
        pandas_df['company'] = pandas_df['company'].str.replace(r'NAGOYA INST TECH [JP]',
                                                                'NAGOYA INSTITUTE OF TECHNOLOGY', regex=True)
        
        #MIE UNIVERSIT
        pandas_df['company'] = pandas_df['company'].str.replace(r'MIE UNIVERSIT.+',
                                                                'MIE UNIVERSITY', regex=True)
        
        #UNIV MICHIGA
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV MICHIGA.+',
                                                                'MICHIGAN STATE UNIVERSITY', regex=True)
        
        #UNIV MICHIGA
        pandas_df['company'] = pandas_df['company'].str.replace(r'UNIV PITTSBURGH COMMONWEALTH SYS HIGHER EDUCATION [US]',
                                                                'UNIVERSITY OF PITTSBURGH', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'RHEOGENE HOLDINGS INC',
                                                                'UNIVERSITY OF PITTSBURGH', regex=True)
        
        #MEDICAL AND BIOLOGICAL LABORATORIES C
        pandas_df['company'] = pandas_df['company'].str.replace(r'MEDICAL AND BIOLOGICAL LABORATORIES C.+',
                                                                'MEDICAL AND BIOLOGICAL LABORATORIES', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'MEDICAL AND BIOLOG LAB CO LTD [JP]',
                                                                'MEDICAL AND BIOLOGICAL LABORATORIES', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'MEDICAL AND BIOLOGICAL LABORATORIES',
                                                                'JSR CORPORATION', regex=True)
        
        
        #MAX PLANCK SOCIETY
        pandas_df['company'] = pandas_df['company'].str.replace(r'MAX PLANCK GE.+',
                                                                'MAX PLANCK SOCIETY', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'MAX-PLANCK-GESELLSCHAFT ZUR FOERDERUNG DER WISSENSCHAFTEN E.V. (DE)',  'MAX PLANCK SOCIETY', regex=True)
        
        #MASSACHUSETTS GEN HOSPITA
        pandas_df['company'] = pandas_df['company'].str.replace(r'MASSACHUSETTS GEN HOSPITA.+',
                                                                'MASSACHUSETTS GEN HOSPITAL', regex=True)
        
        #MARICA
        pandas_df['company'] = pandas_df['company'].str.replace(r'MARICA.+',
                                                                'MARICAL', regex=True)
        
        #LARGE SCALE BIOLOGY CORPORATIO
        pandas_df['company'] = pandas_df['company'].str.replace(r'LARGE SCALE BIOLOGY CORPORATIO.+',
                                                                'LARGE SCALE BIOLOGY CORPORATION', regex=True)
        
        #KNC LABORATORIES C
        pandas_df['company'] = pandas_df['company'].str.replace(r'KNC LABORATORIES C.+',
                                                                'KNC LABORATORIES CO', regex=True)
        
        #KAZUSA DNA RESEARCH INSTITUT
        pandas_df['company'] = pandas_df['company'].str.replace(r'KAZUSA DNA RESEARCH INSTITUT.+',
                                                                'KAZUSA DNA RESEARCH INSTITUTE', regex=True)
        
        #KAPABIOSYSTEMS / ROCHE
        pandas_df['company'] = pandas_df['company'].str.replace(r'KAPABIOSYSTEM.+',
                                                                'KAPABIOSYSTEMS', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'KAPABIOSYSTEMS',
                                                                'ROCHE', regex=True)
        
        #KAGOSHIMA UNIVERSIT
        pandas_df['company'] = pandas_df['company'].str.replace(r'KAGOSHIMA UNIVERSIT.+',
                                                                'KAGOSHIMA UNIVERSITY', regex=True)
        
        #JAPAN INTERNATIONAL RESEARCH CENTER FOR AGRICULTURAL SCIENC
        pandas_df['company'] = pandas_df['company'].str.replace(r'JAPAN INTERNATIONAL RESEARCH CENTER FOR AGRICULTURAL SCIENC.+', 'JAPAN INTERNATIONAL RESEARCH CENTER FOR AGRICULTURAL SCIENCE', regex=True)
        
        #INFECTIO DIAGNOSTI
        pandas_df['company'] = pandas_df['company'].str.replace(r'INFECTIO DIAGNOSTI.+',
                                                                'INFECTIO DIAGNOSTIC INC', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'INFECTIO DIAGNOSTIC INC',
                                                                'BECTON, DICKINSON AND COMPANY', regex=True)
        
        #HIROSHIMA UNIVERSIT
        pandas_df['company'] = pandas_df['company'].str.replace(r'HIROSHIMA UNIVERSIT.+',
                                                                'HIROSHIMA UNIVERSITY', regex=True)
        
        #HENKEL
        pandas_df['company'] = pandas_df['company'].str.replace(r'HENKE.+',
                                                                'HENKEL', regex=True)
        
        #HANGZHOU RUIFENG BIOTECHNOLOG
        pandas_df['company'] = pandas_df['company'].str.replace(r'HANGZHOU RUIFENG BIOTECHNOLOG.+',
                                                                'HANGZHOU RUIFENG BIOTECHNOLOGY', regex=True)
        
        #GILUPI
        pandas_df['company'] = pandas_df['company'].str.replace(r'GILUP.+',
                                                                'GILUPI GMBH', regex=True)
        
        #GENESYS
        pandas_df['company'] = pandas_df['company'].str.replace(r'GENESY.+',
                                                                'GENESYS LTD GB', regex=True)
        
        #GENECOPOEIA
        pandas_df['company'] = pandas_df['company'].str.replace(r'GENECOPOEI.+',
                                                                'GENECOPOEIA', regex=True)
        
        #GENECHEM
        pandas_df['company'] = pandas_df['company'].str.replace(r'GENECHE.+',
                                                                'GENECHEM INC', regex=True)
        
        #GENARIS
        pandas_df['company'] = pandas_df['company'].str.replace(r'GENARI.+',
                                                                'GENARIS INC', regex=True)
        
        #FLUXOME SCIENCE
        pandas_df['company'] = pandas_df['company'].str.replace(r'FLUXOME SCIENCE.+',
                                                                'FLUXOME SCIENCES', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'FLUXOME SCIENCE',
                                                                'EVOLVA', regex=True)
        
        #F. HOFFMANN-LA ROCHE AG
        pandas_df['company'] = pandas_df['company'].str.replace(r'F. HOFFMANN-LA ROCHE AG',
                                                                'F HOFFMANN-LA ROCHE AG', regex=True)
        
        #EVONIK
        pandas_df['company'] = pandas_df['company'].str.replace(r'EVONI.+',
                                                                'EVONIK', regex=True)
        
        #ENZYMATICA
        pandas_df['company'] = pandas_df['company'].str.replace(r'ENZYMATIC.+',
                                                                'ENZYMATICA AB', regex=True)
        
        #ENTERPRISE IRELAN
        pandas_df['company'] = pandas_df['company'].str.replace(r'ENTERPRISE IRELAN.+',
                                                                'ENTERPRISE IRELAND (BIORESEARCH IRELAND)', regex=True)
        
        pandas_df['company'] = pandas_df['company'].str.replace(r'ENTPR IE TRD AS BIORESEAR.+',
                                                                'ENTERPRISE IRELAND (BIORESEARCH IRELAND)', regex=True)
        #DEUTSCHES KREBSFORS
        pandas_df['company'] = pandas_df['company'].str.replace(r'DEUTSCHES KREBSFOR.+',
                                                                'DKFZ', regex=True)
        
        #DAIKIN INDUSTRIES
        pandas_df['company'] = pandas_df['company'].str.replace(r'DAIKIN INDUSTRIE.+',
                                                                'DAIKIN INDUSTRIES', regex=True)
        
        #COMMISSARIAT A L'ENERGIE ATOMIQUE ET AUX ENERGIE
        pandas_df['company'] = pandas_df['company'].str.replace(r'COMMISSARIAT A L\'ENERGIE ATOMIQUE ET AUX ENERGIE.+',
                                                                'COMMISSARIAT A L\'ENERGIE ATOMIQUE ET AUX ENERGIES', regex=True)
        
        #CHEMICON
        pandas_df['company'] = pandas_df['company'].str.replace(r'CHEMICO.+',
                                                                'CHEMICO INTERNATIONAL INC', regex=True)
        
        #CENTRO DE INGENIERA GENTIC
        pandas_df['company'] = pandas_df['company'].str.replace(r'CENTRO DE INGENIERA GENTIC.+',
                                                                'CENTRO DE INGENIERA GENTICA', regex=True)
        
        #CELLECTIS
        pandas_df['company'] = pandas_df['company'].str.replace(r'CELLECTI.+',
                                                                'CELLECTIS', regex=True)
        
        #CARGILL IN
        pandas_df['company'] = pandas_df['company'].str.replace(r'CARGILL IN.+',
                                                                'CARGILL INC', regex=True)
        
        #BRYAN, BRUCE J. (US); PROLUME, LTD. (US)
        pandas_df['company'] = pandas_df['company'].str.replace(r'BRYAN, BRUC.+',
                                                                'BRUCE J BRYAN', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'BRUCE BRYA.+',
                                                                'BRUCE J BRYAN', regex=True)
        
        #BIOTEC PHARMACON ASA
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIOTEC PHARMACON ASA',
                                                                'BIOTECH PHARMACON ASA', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIOTEC PHARMACON ASA',
                                                                'ARCTICZYMES', regex=True)
        
        #BIORIGINAL FOOD AND SCIENCE CORPORATION
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIORIGINAL FOOD & SCIENCE CORP. (CA)',
                                                                'BIORIGINAL FOOD AND SCIENCE CORPORATION', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIORIGINAL FOOD AND SCIENCE CORPORATION',
                                                                'COOKE INC', regex=True)
        
        
        
        #BIOMOLECULAR EN
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIOMOLECULAR EN.+',
                                                                'BIOMOLECULAR ENGINEERING RESEARCH INSTITUTE', regex=True)
        
        #THERMO FISHER SCIENTIFIC
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIOLMAG.+',
                                                                'BIOIMAGE', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIOIMAG.+',
                                                                'BIOIMAGE', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIOIMAGE',
                                                                'THERMO FISHER SCIENTIFIC', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'APPLIED BIOSYSTEMS',
                                                                'THERMO FISHER SCIENTIFIC', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'APPLERA CORPORATION (US)',
                                                                'THERMO FISHER SCIENTIFIC', regex=True)
       
        
        #BIOGASOL
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIOGASO.+',
                                                                'BIOGASOL APS', regex=True)
        
        #BIO ARCHITECTURE
        pandas_df['company'] = pandas_df['company'].str.replace(r'BIO ARCHITECTUR.+',
                                                                'BIO ARCHITECTURE LAB', regex=True)
        
        #BENSON HILL BIOSYSTEM
        pandas_df['company'] = pandas_df['company'].str.replace(r'BENSON HILL BIOSYSTEM.+',
                                                                'BENSON HILL BIOSYSTEMS', regex=True)
        
        #BAXTER INTERNATIONAL
        pandas_df['company'] = pandas_df['company'].str.replace(r'BAXTER INTERNATIONA.+',
                                                                'BAXTER INTERNATIONAL', regex=True)
        
        #AXXAM
        pandas_df['company'] = pandas_df['company'].str.replace(r'AXXA.+',
                                                                'AXXAM SPA', regex=True)
        
        #AVESTHA GEN
        pandas_df['company'] = pandas_df['company'].str.replace(r'AVESTA GE.+',
                                                                'AVESTA GEN', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'AVESTA GE.+',
                                                                'AVESTHA GEN', regex=True)
        
        #ASYMCHEM LABORATORI
        pandas_df['company'] = pandas_df['company'].str.replace(r'ASYMCHEM LABORATOR.+',
                                                                'ASYMCHEM LABORATORIES', regex=True)
        
        #ASTRAZENECA
        pandas_df['company'] = pandas_df['company'].str.replace(r'ASTRAZENECA A.+',
                                                                'ASTRAZENECA AB', regex=True)
        
        #ASAHI
        pandas_df['company'] = pandas_df['company'].str.replace(r'ASAH.+',
                                                                'ASAHI', regex=True)
        
        #AQUABIO PRODUCT
        pandas_df['company'] = pandas_df['company'].str.replace(r'AQUABIO PRODUCT.+',
                                                                'AQUABIO PRODUCTS', regex=True)
        
        #APIT LABORATORIES
        pandas_df['company'] = pandas_df['company'].str.replace(r'APIT LABORATORIE.+',
                                                                'APIT LABORATORIES', regex=True)
        
        #AMERSHA
        pandas_df['company'] = pandas_df['company'].str.replace(r'AMERSHA.+',
                                                                'AMERSHAM UK LTD', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'AMERSHAM UK LTD',
                                                                'GE HEALTHCARE', regex=True)                                   
        
        #ACGT PROGENOMIC
        pandas_df['company'] = pandas_df['company'].str.replace(r'ACGT PROGENOMIC.+',
                                                                'ACGT PROGENOMICS', regex=True)
        
        #YIELD10 BIOSCIENCE
        pandas_df['company'] = pandas_df['company'].str.replace(r'METABOLIX INC. (US)',
                                                                'YIELD10 BIOSCIENCE', regex=True)
                                                                
        #HARVARD MEDICAL SCHOOL
        pandas_df['company'] = pandas_df['company'].str.replace(r'THE GENERAL HOSPITAL CORPORATION',
                                                                'HARVARD MEDICAL SCHOOL', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'MASSACHUSETTS GEN HOSPITAL',
                                                                'HARVARD MEDICAL SCHOOL', regex=True)
                                                                
        #GINKGO
        pandas_df['company'] = pandas_df['company'].str.replace(r'NOVOGY INC [US]',
                                                                'GINKGO', regex=True)
        pandas_df['company'] = pandas_df['company'].str.replace(r'ZYMERGEN INC',
                                                                'GINKGO', regex=True)
                                                                
        #PERSON
        pandas_df['company'] = pandas_df['company'].str.replace(r'IKUO NAKAMURATOSHIYUKI MORIIZUMI',
                                                                'IKUO NAKAMURATO', regex=True)                                                    
        #FUJIFILM                                                         
        pandas_df['company'] = pandas_df['company'].str.replace(r'WAKO PURE CHEMICAL INDUSTRIES LTD',
                                                                'FUJIFILM', regex=True)
                                                                
        #GUARD THERAPEUTICS                                                      
        pandas_df['company'] = pandas_df['company'].str.replace(r'A1M PHARMA AB',
                                                                'GUARD THERAPEUTICS', regex=True)
                                                                
        #PROKAZYME                                                      
        pandas_df['company'] = pandas_df['company'].str.replace(r'PROKARIA EHF. (IS)',
                                                                'PROKAZYME', regex=True)
                                                                
       
                                                                
                                                                
            
    return pandas_df

def calculate_stats_for_companies(pandas_df):
    import numpy as np
    import pandas as pd
    
    head = pandas_df.shape[0]
    highest_num_of_patent_seqs = pandas_df.groupby(by=(["patent_num", "company"]), dropna=False).size().reset_index()
    dfg_visible_num_of_patents = highest_num_of_patent_seqs.groupby(['company']).size().to_frame().sort_values([0], ascending = False).reset_index()
    dfg_visible_num_of_patents.columns = ['company', 'num_of_patents']
    
    highest_num_of_patent_seqs = pandas_df.groupby(by=(['organism', "company"]), dropna=False).size().reset_index()
    dfg_visible_num_of_organisms = highest_num_of_patent_seqs.groupby(['company']).size().to_frame().sort_values([0], ascending = False).reset_index()
    dfg_visible_num_of_organisms.columns = ['company', 'num_of_species']
    
    highest_num_of_patent_seqs = pandas_df.groupby(by=(["origin", "company"]), dropna=False).size().reset_index()
    dfg_visible_num_of_seqs = highest_num_of_patent_seqs.groupby(['company']).size().to_frame().sort_values([0], ascending = False).reset_index()
    dfg_visible_num_of_seqs.columns = ['company', 'num_of_sequences']
    
    highest_num_of_patent_seqs = pandas_df.groupby(by=(["seq_length", "company"]), dropna=False).size().reset_index()
    dfg_visible_num_of_lengths = highest_num_of_patent_seqs.groupby(['company']).size().to_frame().sort_values([0], ascending = False).reset_index()
    dfg_visible_num_of_lengths.columns = ['company', 'num_of_lengths']
    
    dfg_visible_av_length = pandas_df.groupby(['company'])['seq_length'].agg(pd.Series.median).reset_index()
    dfg_visible_av_length.columns = ['company', 'median_seq_length']
    
    dfg_visible_av_year = pandas_df.groupby(['company'])['year'].agg(pd.Series.median).reset_index()
    dfg_visible_av_year.columns = ['company', 'median_year']

    pandas_df = pandas_df.merge(dfg_visible_num_of_seqs, left_on='company', right_on='company', how='outer')
    pandas_df = pandas_df.merge(dfg_visible_num_of_organisms, left_on='company', right_on='company', how='outer')
    pandas_df = pandas_df.merge(dfg_visible_num_of_patents, left_on='company', right_on='company', how='outer')
    pandas_df = pandas_df.merge(dfg_visible_num_of_lengths, left_on='company', right_on='company', how='outer')
    pandas_df = pandas_df.merge(dfg_visible_av_length, left_on='company', right_on='company', how='outer')
    pandas_df = pandas_df.merge(dfg_visible_av_year, left_on='company', right_on='company', how='outer')
    
    
    for_scatter = pandas_df.sort_values(by = ['num_of_sequences', 'num_of_species'], ascending = [False, False])[['company', 'num_of_sequences', 'num_of_species', 'num_of_patents', 'num_of_lengths', 'median_seq_length', 'median_year']].drop_duplicates().head(head)
    for_scatter['log2_species'] = np.log2(for_scatter['num_of_species'])
    for_scatter['log2_sequences'] = np.log2(for_scatter['num_of_sequences'])
    for_scatter['log2_lengths'] = np.log2(for_scatter['num_of_lengths'])
    for_scatter['log2_patents'] = np.log2(for_scatter['num_of_patents'])
    for_scatter['log2_av_length'] = np.log2(for_scatter['median_seq_length'])
    for_scatter['seq2species'] = for_scatter['num_of_sequences']/for_scatter['num_of_species']
    for_scatter['seq2patents'] = for_scatter['num_of_sequences']/for_scatter['num_of_patents']
    
    return for_scatter


def calculate_stats_for_companies(pandas_df):
    import numpy as np
    import pandas as pd
    from Bio.Seq import Seq
    
    head = pandas_df.shape[0]
    highest_num_of_patent_seqs = pandas_df.groupby(by=(["patent_num", "company"]), dropna=False).size().reset_index()
    dfg_visible_num_of_patents = highest_num_of_patent_seqs.groupby(['company']).size().to_frame().sort_values([0], ascending = False).reset_index()
    dfg_visible_num_of_patents.columns = ['company', 'num_of_patents']
    
    highest_num_of_patent_seqs = pandas_df.groupby(by=(['organism', "company"]), dropna=False).size().reset_index()
    dfg_visible_num_of_organisms = highest_num_of_patent_seqs.groupby(['company']).size().to_frame().sort_values([0], ascending = False).reset_index()
    dfg_visible_num_of_organisms.columns = ['company', 'num_of_species']
    
    highest_num_of_patent_seqs = pandas_df.groupby(by=(["origin", "company"]), dropna=False).size().reset_index()
    dfg_visible_num_of_seqs = highest_num_of_patent_seqs.groupby(['company']).size().to_frame().sort_values([0], ascending = False).reset_index()
    dfg_visible_num_of_seqs.columns = ['company', 'num_of_sequences']
    
    highest_num_of_patent_seqs = pandas_df.groupby(by=(["seq_length", "company"]), dropna=False).size().reset_index()
    dfg_visible_num_of_lengths = highest_num_of_patent_seqs.groupby(['company']).size().to_frame().sort_values([0], ascending = False).reset_index()
    dfg_visible_num_of_lengths.columns = ['company', 'num_of_lengths']
    
    dfg_visible_av_length = pandas_df.groupby(['company'])['seq_length'].agg(pd.Series.median).reset_index()
    dfg_visible_av_length.columns = ['company', 'median_seq_length']
    
    dfg_visible_av_year = pandas_df.groupby(['company'])['year'].agg(pd.Series.median).reset_index()
    dfg_visible_av_year.columns = ['company', 'median_year']
    
    dfg_visible_av_year = pandas_df.groupby(['company'])['year'].agg(pd.Series.median).reset_index()
    dfg_visible_av_year.columns = ['company', 'median_year']
    
    pandas_df['protein_origin'] = pandas_df.origin.apply(lambda x: str(Seq(x).translate()))
    pandas_df['num_of_stop_codons'] = pandas_df.protein_origin.str.count("\*")
    pandas_df['valid_protein'] = np.where((pandas_df['num_of_stop_codons']<=1)&(pandas_df['seq_length']>=150), True, False)
    test1 = pandas_df.groupby(['company'])['valid_protein'].agg(pd.Series.sum).reset_index()
    test1.columns = ['company', 'valid_proteins_counts']
    test2 = pandas_df.groupby(['company'])['valid_sequence'].agg(pd.Series.sum).reset_index()
    test2.columns = ['company', 'valid_sequences_counts']

    dfg_visible_valid_proteins = pd.merge(test1, test2, on='company', how='outer')
    dfg_visible_valid_proteins['% of proteins'] = dfg_visible_valid_proteins['valid_proteins_counts']/dfg_visible_valid_proteins['valid_sequences_counts']
    #test3.sort_values(by='valid_proteins_counts', ascending = False).head(50)
    dfg_visible_valid_proteins = dfg_visible_valid_proteins[['company', '% of proteins']]

    pandas_df = pandas_df.merge(dfg_visible_num_of_seqs, left_on='company', right_on='company', how='outer')
    pandas_df = pandas_df.merge(dfg_visible_num_of_organisms, left_on='company', right_on='company', how='outer')
    pandas_df = pandas_df.merge(dfg_visible_num_of_patents, left_on='company', right_on='company', how='outer')
    pandas_df = pandas_df.merge(dfg_visible_num_of_lengths, left_on='company', right_on='company', how='outer')
    pandas_df = pandas_df.merge(dfg_visible_av_length, left_on='company', right_on='company', how='outer')
    pandas_df = pandas_df.merge(dfg_visible_av_year, left_on='company', right_on='company', how='outer')
    pandas_df = pandas_df.merge(dfg_visible_valid_proteins, left_on='company', right_on='company', how='outer')
    
    
    for_scatter = pandas_df.sort_values(by = ['num_of_sequences', 'num_of_species'], ascending = [False, False])[['company', 'num_of_sequences', 'num_of_species', 'num_of_patents', 'num_of_lengths', 'median_seq_length', 'median_year', '% of proteins']].drop_duplicates().head(head)
    for_scatter['log2_species'] = np.log2(for_scatter['num_of_species'])
    for_scatter['log2_sequences'] = np.log2(for_scatter['num_of_sequences'])
    for_scatter['log2_lengths'] = np.log2(for_scatter['num_of_lengths'])
    for_scatter['log2_patents'] = np.log2(for_scatter['num_of_patents'])
    for_scatter['log2_av_length'] = np.log2(for_scatter['median_seq_length'])
    for_scatter['seq2species'] = for_scatter['num_of_sequences']/for_scatter['num_of_species']
    for_scatter['seq2patents'] = for_scatter['num_of_sequences']/for_scatter['num_of_patents']
    
    return for_scatter
    