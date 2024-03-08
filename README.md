# Novel Database Reveals Growing Prominence of Deep-Sea Life for Marine Bioprospecting

*Erik Zhivkoplias, Agnes Pranindita, Paul Dunshirn, Jean-Baptiste Jouffray, Robert Blasiak (2024)*

## Introduction

The MABPAT dataset aims to provide valuable insights into the scope and scale of marine bioprospecting. It offers the research and practitioner community direct access to marine genetic sequences submitted to patent bureaus, highlighting their potential to encode biological functions, species taxonomy, type of applicant, and other relevant information crucial for discussions on the access and utilization of marine genetic resources.

For more details about the dataset, please refer to the [manuscript](https://www.researchsquare.com/article/rs-3136354/v1).

## Download and Install Conda

Download and install the latest Anaconda / Miniconda for your operating system. An example for Linux is provided below:

```bash
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source .bashrc
```

### Clone Repository and Install Conda Environment

Begin by cloning this GitHub repository:

```bash
git clone https://github.com/zhivkoplias/mabpat
cd mabpat/analysis/env
```

Proceed with the Conda environment installation:

```bash
conda create --name mgr --file mgr_env.yml
conda activate mgr
```

## Usage

Scripts used are located in the `mabpat/analysis/src` folder. Scripts for the development of the Shiny app ([MABPAT Shiny App](https://mabpat.shinyapps.io/main/)) and ([SQLite database](http://mabpat.fly.dev/MABPAT_dataset)) are based in their respective folders.
