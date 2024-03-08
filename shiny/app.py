
# import libs
import pandas as pd # noqa: F401 (this line needed for Shinylive to load plotly.express)
import plotly.express as px
import plotly.graph_objs as go

import matplotlib.pyplot as plt
import numpy as np
from shiny import *
from shinywidgets import output_widget, render_widget, register_widget
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import dash
import dash_html_components as html

import os
from functools import reduce
import asyncio

from shiny import App, reactive, render, req, session, ui

# load data
#mabpat_df = pd.read_csv("MABPAT_with_unknown_proteins_141123_COMPLETED.csv.bz2", encoding="utf8", compression='bz2') 
mabpat_df_bck = pd.read_feather("MABPAT_with_unknown_proteins_141123_COMPLETED_t.feather")
mabpat_df = mabpat_df_bck[['Applicant', 'Applicant type', 'Applicant country',
                          'Year of application', 'Application number', 'Patent system',
                          'Sequence id', 'Species name', 'Domain', 'Phylum', 'Is Deep-sea', 'Deep-sea source',
                          'Is marine sequence', 'Sequence status', 'Is protein-coding sequence', 'appearance']]

mabpat_df['appearance'] = 1
#options to select from
options_country = mabpat_df['Applicant country'].unique().tolist()
options_jurisdiction = mabpat_df['Patent system'].unique().tolist()

mabpat_df_type_choices = mabpat_df[mabpat_df['Applicant type'] != 'NONE']
options_applicant_type = mabpat_df_type_choices['Applicant type'].unique().tolist()
#options_applicant_type = mabpat_df['Applicant type'].unique().tolist()

############## APP_UI ###############

app_ui = ui.page_navbar(
    
    ui.nav("About", ui.output_ui("data_intro")),
    
    ui.nav("Marine species of interest",  output_widget("plot_sankey"),
        
        ui.panel_fixed(
        ui.input_select("top_actors", "Patent applicants", choices=["top 10", "top 30", "top 50"]),
        ui.input_select("taxonomy", "Taxonomic level", choices=["Domain", "Phylum"]),
        ui.input_checkbox("sequences", "Including predictions", value = True)
        )
        
        ),
    
    
    ui.nav("Applicant types", output_widget("actors"),
           
           ui.panel_fixed(
           ui.input_select("actors_top_actors", "Patent applicants", choices=["top 10", "top 30", "top 50",
                                                                       "top 100", "all"]),
           ui.input_checkbox("actors_sequences", "Including predictions", value = True)
           )
          
           
           ),
    
    
    ui.nav("Applicant countries", ui.output_plot("states"),
           
           ui.page_fluid(
           ui.input_select("states_top_actors", "Patent applicants", choices=["top 10", "top 30", "top 50",
                                                                       "top 100", "all"]),
           ui.input_checkbox("states_sequences", "Including predictions", value = True)
           )
          
           
           ),
    
    ui.nav('Patent applications over time', ui.page_fluid(
    ui.input_slider("n", "Time period", 1980, 2023, 1),
    ui.output_plot("plot_interest"),
    
    ui.input_selectize(
        "countries", "Select country", multiple=True, choices=options_country),
    ui.input_selectize(
        "patents", "Select patent system", multiple=True, choices=options_jurisdiction),
    ui.input_selectize(
        "applicant_type", "Select applicant type", multiple=True, choices=options_applicant_type),

)),
    #ui.download_button("download_selected", "Download selected entries"),
    
    #ui.nav("Download dataset",ui.output_ui("data_download")),

   
 #ui.output_table("table"),
   
    

        
    title='MArine Bioprospecting PATent dataset'
)

############## APP_SERVER ###############

               
def server(input, output, session):
    
    @output
    #@render_widget
    @render.plot(alt="A barplot")
    
    def states():
        import matplotlib.pyplot as plt
        import seaborn as sns

        mabpat_df_states = mabpat_df[mabpat_df['Is marine sequence'] == 1]
        mabpat_df_states = mabpat_df_states[['Applicant country', 'Applicant', 'Application number',
                                             'Patent system', 'Sequence status', 'appearance']]
        
        if not input.states_sequences():
            mabpat_df_states = mabpat_df_states[mabpat_df_states['Sequence status'] == 'observed']
            
        largest_all = mabpat_df_states.drop_duplicates(subset='Application number',
                                    keep='first').groupby('Applicant').sum().reset_index().sort_values(by='appearance',
                                                        ascending=False)

        if input.states_top_actors() == "top 10":
            size_of_top = 10     
        elif input.states_top_actors() == "top 30":
            size_of_top = 30
        elif input.states_top_actors() == "top 50":
            size_of_top = 50
        elif input.states_top_actors() == "top 100":
            size_of_top = 100   
        else:
            size_of_top = len(largest_all.Applicant)
        
        largest_all_companies = largest_all.Applicant.head(size_of_top).to_list()
        top_corporates = mabpat_df_states[mabpat_df_states.Applicant.isin(largest_all_companies)]
        
        top_corporates = top_corporates.drop_duplicates(subset='Application number',
                                    keep='first')
        top_corporates['appearance'] = 1
        
        #plot1
        top_corporates_a = top_corporates[['Applicant country', 'Patent system', 'appearance']]
        top_corporates_a.columns = ['Applicant country', 'Patent_system', 'appearance']
        all_grouped = top_corporates_a.groupby(['Applicant country', 'Patent_system']).sum().reset_index()
        all_grouped_ep = all_grouped[all_grouped.Patent_system == 'EPO'][['Applicant country', 'appearance']]
        all_grouped_jp = all_grouped[all_grouped.Patent_system == 'JPO'][['Applicant country', 'appearance']]
        all_grouped_kr = all_grouped[all_grouped.Patent_system == 'KIPO'][['Applicant country', 'appearance']]
        all_grouped_wo = all_grouped[all_grouped.Patent_system == 'WIPO'][['Applicant country', 'appearance']]
        all_grouped_us = all_grouped[all_grouped.Patent_system == 'USPTO'][['Applicant country', 'appearance']]
        all_grouped_ep.columns = ['Applicant country', 'European Patent Office (EPO)']
        all_grouped_jp.columns = ['Applicant country', 'Patent Office of Japan (JPO)']
        all_grouped_kr.columns = ['Applicant country', 'Korean Intellectual Property Office (KIPO)']
        all_grouped_wo.columns = ['Applicant country', 'World Intellectual Property Organization (WIPO)']
        all_grouped_us.columns = ['Applicant country', 'United States Patent and Trademark Office (USPTO)']
        all_grouped_done = reduce(lambda  left,right: pd.merge(left,right,on=['Applicant country'],
                                    how='outer'), [all_grouped_us,
                                                   all_grouped_wo, all_grouped_kr,
                                                  all_grouped_jp, all_grouped_ep])
        all_grouped_done = all_grouped_done.fillna(0)
        all_grouped_done['sum'] = all_grouped_done.drop('Applicant country', axis=1).sum(axis=1)
        all_grouped_done = all_grouped_done.sort_values(by='sum', ascending=False)
        all_grouped_done = all_grouped_done.drop('sum', axis=1)
        
        from matplotlib import rcParams
        rcParams['figure.figsize'] = 11.7,8.27

        #sns.set_style("whitegrid")
        sns.set(rc={'figure.figsize':(8,14)})
        #sns.set_theme(rc={'figure.figsize':(15,12)})
        sns.set_style("whitegrid")
        #fig, axes = plt.subplots(1, 1)

        #all_grouped_done = all_grouped_done.set_index('country')
        #create chart in each subplot
        seaborn_plt = all_grouped_done.set_index('Applicant country').plot(kind='bar',
                                                                 stacked=True, color=['gray', 'darkorange',
                                                                                  'olive', 'red', 'darkcyan'])
        seaborn_plt.set(xlabel='Applicant country',
               ylabel='Number of patents')

        #sns.set_theme(rc={'figure.figsize':(15,12)})
        return
        
        #plt.show()
        #sns.barplot(data=all_grouped_done, stacked=True, color=['steelblue', 'red',
        #                                                        'green', 'magenta'], ax=axes[0])
        
        #entries_by_year_abs_values = mabpat_df_plot.groupby(['country', 'year']).sum()
        #sns.lineplot(data=entries_by_year_abs_values, x="year", y="appearance", hue='country', ax=axes[1])
        #sns.ecdfplot(data=mabpat_df_plot, x="year", hue="country")

    @output
    @render.plot(alt="A histogram")
        
    def plot_interest():
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set(rc={'figure.figsize':(12,3)})
        try:
            mabpat_df_plot=mabpat_df[mabpat_df['Is marine sequence']==1]
            mabpat_df_plot=mabpat_df_plot.sort_values(by='Year of application', ascending=True)
            mabpat_df_plot = mabpat_df_plot.drop_duplicates(subset=['Application number'], keep='first')
            mabpat_df_plot['appearance'] = 1
            mabpat_df['Year of application'] = mabpat_df['Year of application'].apply(float)
            
            start_year = input.n()

            # Set default values for country, patent system, and applicant type
            default_country = ['GERMANY']
            default_patent_system = ['WIPO']
            default_applicant_type = ['MULTINATIONAL']

            # Filter data with default categories if no user input is provided
            if not input.countries():
                mabpat_df_plot = mabpat_df_plot[(mabpat_df_plot['Applicant country'].isin(default_country))&
                                       (mabpat_df_plot['Patent system'].isin(default_patent_system))&
                                       (mabpat_df_plot['Applicant type'].isin(default_applicant_type))]
                mabpat_df_plot = mabpat_df_plot[mabpat_df_plot['Year of application']>=start_year]
            else:
                mabpat_df_plot = mabpat_df_plot[(mabpat_df_plot['Applicant country'].isin(input.countries()))&
                                       (mabpat_df_plot['Patent system'].isin(input.patents()))&
                                       (mabpat_df_plot['Applicant type'].isin(input.applicant_type()))]
            #mabpat_df_plot = mabpat_df[mabpat_df.patent.isin(input.patents())]
                mabpat_df_plot = mabpat_df_plot[mabpat_df_plot['Year of application']>=start_year]
            
            sns.set_style("whitegrid")
            fig, axes = plt.subplots(1, 2)
    
            #create chart in each subplot
            cummulative_interest = sns.ecdfplot(data=mabpat_df_plot, x="Year of application", hue="Applicant country", ax=axes[1])
            cummulative_interest.set(xlabel='Year of application',
                   ylabel='Cummulative ratio')
            
            entries_by_year_abs_values = mabpat_df_plot.groupby(['Applicant country', 'Year of application']).sum()
            interest_in_values = sns.lineplot(data=entries_by_year_abs_values, x="Year of application", y="appearance", hue='Applicant country', ax=axes[0])
            interest_in_values.set(xlabel='Year of application',
                   ylabel='Number of applications')
            return
        except TypeError:
            pass
  
    @output
    @render_widget
    #@render.plot(alt="A histogram")
    
    def actors():
        mabpat_df_actors = mabpat_df[mabpat_df['Is marine sequence'] == 1]
        
        if not input.actors_sequences():
            mabpat_df_actors = mabpat_df_actors[mabpat_df_actors['Sequence status'] == 'observed']
        
        largest_all = mabpat_df_actors.drop_duplicates(subset='Application number',
                                    keep='first').groupby('Applicant').sum().reset_index().sort_values(by='appearance',
                                                        ascending=False)

        if input.actors_top_actors() == "top 10":
            size_of_top = 10     
        elif input.actors_top_actors() == "top 30":
            size_of_top = 30
        elif input.actors_top_actors() == "top 50":
            size_of_top = 50
        elif input.actors_top_actors() == "top 100":
            size_of_top = 100   
        else:
            size_of_top = len(largest_all.Applicant)
            
        #size_of_top = 100
        
        largest_all_companies = largest_all.Applicant.head(size_of_top).to_list()
        top_corporates = mabpat_df_actors[mabpat_df_actors.Applicant.isin(largest_all_companies)]
        
        top_corporates = top_corporates.drop_duplicates(subset='Application number',
                                    keep='first')
        top_corporates['appearance'] = 1
        
        value_mult = top_corporates[top_corporates['Applicant type']=='MULTINATIONAL'].appearance.sum()
        value_u = top_corporates[top_corporates['Applicant type']=='UNIVERSITY'].appearance.sum()
        value_n = top_corporates[top_corporates['Applicant type']=='NATIONAL'].appearance.sum()
        value_gov = top_corporates[top_corporates['Applicant type']=='GOVERNMENT'].appearance.sum()
        all_values = [value_mult, value_u, value_n, value_gov]
        
        
        fig = make_subplots(1, 1, specs=[[{'type':'pie'}]],
                    horizontal_spacing = 0.05,
                   vertical_spacing = 0.05)


        fig.add_trace(go.Pie(labels=['Multinational company', 'University', 'National company', 'Government'], values=[all_values[0],
                                                                                                       all_values[1],
                                                                                                       all_values[2],all_values[3]]*5, hole=.5,
                     title=''+''+str(int(np.round(sum([all_values[0],all_values[1],all_values[2],all_values[3]]),0)))+(' patents'),
                      scalegroup='one'*2),
                      row=1, col=1)


        fig.update_layout(xaxis_title="%",
        font=dict(
        family="Times New Roman",
        size=24,
        color="Black"
    ), paper_bgcolor="rgba(255,255,255,1)", plot_bgcolor="rgba(255,255,255,1)")

        fig.update_traces(insidetextorientation='horizontal', rotation=52)

        fig.update_traces(
        marker_colors=['#862780', '#0d955f','#dc706b','pink'],
    )
        fig.layout.height = 600
        return fig
    
    @output
    @render_widget
    def plot_sankey():
        mabpat_df_sankey = mabpat_df[mabpat_df['Is marine sequence'] == 1]
        mabpat_df_sankey['appearance'] = 1
        
        if not input.sequences():
            mabpat_df_sankey = mabpat_df_sankey[mabpat_df_sankey['Sequence status'] == 'observed']

        largest_all = mabpat_df_sankey.drop_duplicates(subset='Application number',
                                    keep='first').groupby('Applicant').sum().reset_index().sort_values(by='appearance',
                                                        ascending=False)
                                                                                                     
        if input.top_actors() == "top 10":
            size_of_top = 10     
        elif input.top_actors() == "top 30":
            size_of_top = 30
        elif input.top_actors() == "top 50":
            size_of_top = 50                                        
                                                                                                     
        largest_all_companies = largest_all.Applicant.head(size_of_top).to_list()
        soi_df = mabpat_df_sankey[mabpat_df_sankey['Is marine sequence']==1]
        soi_df = soi_df[soi_df.Applicant.isin(largest_all_companies)]
        

        soi_df['Is Deep-sea'] = soi_df['Is Deep-sea'].apply(str)
        soi_df['Is Deep-sea'] = soi_df['Is Deep-sea'].replace(['0.0'],'Non deep-sea')
        soi_df['Is Deep-sea'] = soi_df['Is Deep-sea'].replace(['1.0'],'Deep-sea')
        soi_df.Domain = soi_df.Domain.apply(str)
        soi_df = soi_df[soi_df.Domain != 'NA']
        soi_df = soi_df[soi_df.Domain != 'Nan']
        soi_df = soi_df[soi_df['Is Deep-sea'] != 'nan']
        soi_df.Domain = soi_df.Domain.replace(['Virus'],'Viruses')
        soi_df = soi_df.drop_duplicates(subset=['Applicant', 'Species name'],
                                    keep='first')
        #soi_df = soi_df[soi_df.Deep_sea == 'Deep-sea']

        soi_df.Domain = soi_df.Domain.apply(str)
        #soi_df.Domain = soi_df.Domain.apply(lambda x: x.upper())
            
        soi_df = soi_df.sort_values('Year of application', ascending = False)
                
        vals = soi_df.groupby(['Application number', input.taxonomy()]).size().to_frame().sort_values([0], ascending = False).reset_index()[0].to_list()
        keys = soi_df.groupby(['Application number', input.taxonomy()]).size().to_frame().sort_values([0], ascending = False).reset_index()[input.taxonomy()].to_list()
        org_pop = dict(zip(keys, vals))

        soi_df['type_popularity'] = soi_df[input.taxonomy()].map(org_pop)

        soi_df = soi_df.sort_values('Year of application', ascending = False)



        pandas_df_gb = soi_df.groupby([input.taxonomy(), 'Is Deep-sea', 'Applicant', 'Applicant country']).size().reset_index(name='Freq')

        pandas_df_gb = pandas_df_gb.sort_values('Freq', ascending = False)
            #print(pandas_df_gb)
            
        df3 = (
            pd.concat(
                [
                    pandas_df_gb.loc[:, [c1, c2] + ["Freq"]].rename(
                        columns={c1: "source", c2: "target"}
                    )
                    for c1, c2 in zip(pandas_df_gb.columns[:-1], pandas_df_gb.columns[1:-1])
                ]
            )
            .groupby(["source", "target"], as_index=False)
            .sum()
        )

        df3.source = df3.source.apply(str)
        df3.target = df3.target.apply(str)
            
        nodes = np.unique(df3[["source", "target"]], axis=None)
            
        nodes = pd.Series(index=nodes, data=range(len(nodes)))
            
        color = ["#449464","#80391e","purple","#b97455","purple",
                    "purple","purple","purple","#4b66a1","purple",
                    "#e07b39","red","purple","#449464","orange", "purple",
                    "yellow","#8aaeda","purple","blue","black"]
        
        color = ["#b97455"] * len(nodes)
        
        fig = go.Figure(
        go.Sankey(arrangement='freeform',
                 node={"pad": 40, "label": nodes.index, "color": color},
                 link={
                     "source": nodes.loc[df3["source"]],
                     "target": nodes.loc[df3["target"]],
                     "value": df3["Freq"],
                 },
             )
         )
 
        fig.update_layout(hovermode = 'x',
                              font=dict(
                     color='#051c2c'), font_size=14),
        fig.layout.height = 600
        
        fig.layout.xaxis.fixedrange = False
        fig.layout.yaxis.fixedrange = False
        
        return fig
    
    @output(id="data_intro")
    @render.ui
    def _():

        md = ui.markdown(
            f"""
## MArine Bioprospecting PATent (MABPAT) dataset 
<img src="https://figshare.com/ndownloader/files/44697043/preview/44697043/preview.jpg" width="500" height="296" align="left">

The goal of the MABPAT dataset is to provide a useful insight into the scope and scale of marine bioprospecting.
We offer the research and practitioner community direct access to marine genetic sequences submitted
to patent bureaus, their potential to encode biological functions, species taxonomy, type of applicant,
and other information that might be relevant for the discussion on the access and utilization
of marine genetic resources.
   
The dataset contains 60,631 protein-coding sequences of marine origin that were 
previously unidentified, and linked to 2,257 patent applications. To incorporate these patent applications into the
 visual summary statistics of the MABPAT, select the "including predictions" option.

The MABPAT dataset is organized as an SQLite database that includes seven interconnected tables and three views, designed to be user-friendly for both researchers and practitioners. Below is a brief overview of what each table and view includes:

### Tables Overview

- **Applicants Table**: Tracks patent applicants, including the applicant's name, type, and country of origin.

- **Applications Table**: Contains details on each patent application related to marine genetic sequences, including the application number, filing date, and patent system.

- **Marine Species Table**: Lists marine species linked to the genetic sequences in the dataset, providing species names, taxonomic classification, and deep-sea status.

- **Sequences Table**: Shows genetic sequences and indicates whether they are from marine species.

- **Applications_Sequences Table**: Connects patent applications to specific genetic sequences, useful for identifying which sequences are mentioned in patents.

- **Marine Sequences Table**: Offers detailed information on each marine genetic sequence, including GC content, sequence length, and protein-coding status.

- **Marine Sequences_Protein_Annotations Table**: Provides annotations for protein-coding sequences, adding further value.

### Views Overview

- **View_MarineSequences_Applicants**: Joins Marine Sequences, Applications_Sequences, Applications, and Applicants tables to provide information on genetic sequences, applicants, and patent applications.

- **View_MarineSequences_Species**: Joins Marine Sequences and Marine_Species tables to offer insights into genetic sequences and associated marine species.

- **View_MarineSequences_Annotations**: Connects Marine Sequences and Marine_Sequences_Protein_Annotations tables to provide annotations for protein-coding sequences.

### Download

The MABPAT dataset is a available for download ([SQLite database](https://figshare.com/ndownloader/files/44714050), [CSV file](https://figshare.com/ndownloader/files/44714047)) and through [an interactive web interface](http://mabpat.fly.dev/MABPAT_dataset).

The interactive form is hosted by an open-source tool, [Datasette.io](https://datasette.io/), which aims to streamline the process of turning data stored in SQLite databases into interactive, web-accessible resource. Datasette supports faceted and keyword search, enabling users to filter datasets by multiple criteria simultaneously, as well as executing SQL queries directly through the Datasette interface. It also allows the export of selected entries in a form of CSV. Despite its ease of use and the fact that it doesn't require technical expertise in web development or database management, a quick tutorial on how to navigate Datasette for data exploration is available [here](https://datasette.io/tutorials/explore).

Additionally, we provide [a FASTA file](https://figshare.com/ndownloader/files/44697046) with all nucleoide sequences included in the MABPAT.

The diagram below offers a consolidated view of data from different tables. For further details regarding the dataset please refer to the [manuscript](https://doi.org/10.21203/rs.3.rs-3136354/v1).

<img src="https://figshare.com/ndownloader/files/44697040/preview/44697040/preview.jpg" width="651" height="549">

#### Citation

***To cite the MABPAT content, please use:***

-   Erik Zhivkoplias, Agnes Pranindita, Paul Dunshirn et al.
    Novel database reveals growing prominence of deep-sea life for marine bioprospecting,
    05 October 2023, PREPRINT (Version 1)
    <https://doi.org/10.21203/rs.3.rs-3136354/v1>

<sup>****The MABPAT draws upon the following data sources:****</sup>

<sup>*****International Nucleotide Sequence Database Collaboration (INSDC)*****</sup>

<sup> - Arita M, Karsch-Mizrachi I, Cochrane G. The international nucleotide sequence
    database collaboration. Nucleic Acids Res. 2021 Jan 8;49(D1):D121-D124.
    <https://doi:10.1093/nar/gkaa967>
    Accessed 2022-11-15.</sup>
    
<sup>*****UniProtKB*****</sup>

<sup> - The UniProt Consortium et al. UniProt: the Universal Protein Knowledgebase in 2023.
    Nucleic Acids Research, 51, 523–531 (2023).
    <https://doi.org/10.1093/nar/gkac1052>
    Accessed 2023-10-25.</sup>

<sup>*****World Register of Marine Species (WoRMS)*****</sup>

<sup> - WoRMS Editorial Board (2023). World Register of Marine Species. Available from
    https://www.marinespecies.org at VLIZ.
    <https://doi:10.14284/170>
    Accessed 2022-11-15.</sup>

<sup>*****World Register of Deep-Sea species (WoRDSS)*****</sup>

<sup> - Glover, A.G., Higgs, N., and Horton, T. (2023). World Register of Deep-Sea species
    (WoRDSS). 
    <https://doi:10.14284/352>
    Accessed 2022-11-15.</sup>

(c) [Erik Zhivkoplias](https://www.stockholmresilience.org/meet-our-team/staff/2022-06-08-zhivkoplias.html), 11-2023. Database is available under a
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license.

            """,
        )

        return ui.div(md, class_="my-3 lead")
    
    @output
    @render_widget
    
    def my_widget():
        df = px.data.tips()
        fig = px.histogram(
            df, x=input.x(), color=input.color(),
            marginal="rug"
        )
        fig.layout.height = 1200
        return fig
    
    @output
    @render.data_frame
    def summary_data():
        
        mabpat_df_head = mabpat_df[mabpat_df['Is marine sequence'] == 1]
        #mabpat_df_head = mabpat_df
        mabpat_df_head = mabpat_df_head[['Applicant', 'Applicant type', 'Applicant country', 'Year of application',
                                         'Application number', 'Patent system', 'Species name', 'Sequence id']]  #organisms[lst]+sequences[lst]
        
        mabpat_df_head = mabpat_df_head.groupby(['Applicant', 'Applicant type', 'Applicant country', 'Year of application',
                                         'Application number', 'Patent system']).aggregate(lambda tdf: tdf.unique().tolist()).reset_index()
        mabpat_df_head.columns = ['Applicant', 'Applicant type', 'Applicant country',
                                  'Year of application', 'Application number', 'Patent system',
                                  'Species names', 'Sequence ids']

        
        height = 350 if input.fixedheight() else None
        width = "100%" if input.fullwidth() else "fit-content"
        
        ui.output_ui("download_selected")
        
        return render.DataGrid(
                mabpat_df_head,
                row_selection_mode=input.selection_mode(),
                height=height,
                width=width,
                filters=input.filters(),
            )

    
    @output
    @render.data_frame()
    def table():
        
        mabpat_df_head = mabpat_df[mabpat_df['Is marine sequence'] == 1]
        mabpat_df_head['Year of application'] = mabpat_df_head['Year of application'] .apply(float)
        #mabpat_df_head = mabpat_df
        mabpat_df_head = mabpat_df_head[['Applicant', 'Applicant type', 'Applicant country', 'Year of application',
                                         'Application number', 'Patent system', 'Species name', 'Sequence id']]  #organisms[lst]+sequences[lst]
        
        mabpat_df_head = mabpat_df_head.groupby(['Applicant', 'Applicant type', 'Applicant country', 'Year of application',
                                         'Application number', 'Patent system']).aggregate(lambda tdf: tdf.unique().tolist()).reset_index()
        mabpat_df_head.columns = ['Applicant', 'Applicant type', 'Applicant country',
                                  'Year of application', 'Application number', 'Patent system',
                                  'Species names', 'Sequence ids']
        #mabpat_df_head.Deep_sea = mabpat_df_head.Deep_sea.apply(str)
        #mabpat_df_head.marine_sequence = mabpat_df_head.marine_sequence.apply(str)
        #mabpat_df_head.id = mabpat_df_head.id.apply(str)
        
        height = 350 if input.fixedheight() else None
        width = "100%" if input.fullwidth() else "fit-content"
        
        ui.output_ui("download_selected")

        return render.DataGrid(
                mabpat_df_head,
                row_selection_mode=input.selection_mode(),
                height=height,
                width=width,
                filters=input.filters(),
            )
        
        
        
        #return mabpat_df.head(10)
    @reactive.Calc
    def filtered_df():
        selected_idx = list(req(input.table_selected_rows()))
        selected_patents = mabpat_df_head.iloc[selected_idx]["Application number"]
        selected_df = mabpat_df_head[mabpat_df_head["Application number"].isin(selected_patents)]
        selected_df.to_csv('selected.csv', index=False)
        
        return selected_df
    
    @session.download(
        filename=lambda: f"{np.random.randint(100,999)}.csv"
        )
    async def download_selected():
            
        d = {'col1': [1, 2, 3], 'col2': [4, 5, 6]}

        df = pd.DataFrame(d)
           
        #df.to_csv('selected.csv', index=False)
        await asyncio.sleep(0.25)
        yield selected_df.head(10).to_string()

    @output(id="data_download")
    @render.ui
    def _():

        md_dwnld = ui.markdown(
            f"""  
The MABPAT dataset is a available for download ([SQLite database](https://figshare.com/ndownloader/files/44714050), [CSV file](https://figshare.com/ndownloader/files/44714047)) and through [an interactive web interface](http://mabpat.fly.dev/).

The interactive form is hosted by an open-source tool, [Datasette.io](https://datasette.io/), which aims to streamline the process of turning data stored in SQLite databases into interactive, web-accessible resource. Datasette supports faceted and keyword search, enabling users to filter datasets by multiple criteria simultaneously, as well as executing SQL queries directly through the Datasette interface. It also allows the export of selected entries in a form of CSV. Despite its ease of use and the fact that it doesn't require technical expertise in web development or database management, a quick tutorial on how to navigate Datasette for data exploration is available [here](https://datasette.io/tutorials/explore).

Additionally, we provide [a FASTA file](https://figshare.com/ndownloader/files/44697046) with all nucleoide sequences included in the MABPAT.
            """,
        )

        return ui.div(md_dwnld)

    @output
    @render.data_frame
    
    def grid():
        height = 350 if input.fixedheight() else None
        width = "100%" if input.fullwidth() else "fit-content"
        if input.gridstyle():
            return render.DataGrid(
                mabpat_df,
                row_selection_mode=input.selection_mode(),
                height=height,
                width=width,
            )
        else:
            return render.DataTable(
                mabpat_df,
                row_selection_mode=input.selection_mode(),
                height=height,
                width=width,
            )

    @output
    @render.text
    def detail():
        if (
            input.grid_selected_rows() is not None
            and len(input.grid_selected_rows()) > 0
        ):
            # "split", "records", "index", "columns", "values", "table"
            return mabpat_df.iloc[list(input.grid_selected_rows())]
        
# This is a hacky workaround to help Plotly plots automatically
# resize to fit their container. In the future we'll have a
# built-in solution for this.
def synchronize_size(output_id):
    def wrapper(func):
        input = session.get_current_session().input

        @reactive.Effect
        def size_updater():
            func(
                input[f".clientdata_output_{output_id}_width"](),
                input[f".clientdata_output_{output_id}_height"](),
            )

        # When the output that we're synchronizing to is invalidated,
        # clean up the size_updater Effect.
        reactive.get_current_context().on_invalidate(size_updater.destroy)

        return size_updater

    return wrapper
        

app = App(app_ui, server, debug=True)
