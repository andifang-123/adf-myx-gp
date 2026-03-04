# Resource-to-Need Alignment in Chicago Public Schools (CPS)

---

## 📌 Project Overview

This project investigates whether **school resource allocation aligns with structural student disadvantage** across Chicago Public Schools (CPS).

We construct two composite indices:

- **Resource Index (RI)** — institutional + physical capacity  
- **Opportunity Index (OI)** — cumulative student disadvantage  

We evaluate:
- Spatial inequality patterns across Chicago communities
- The relationship between disadvantage and academic performance
- Whether higher-need schools receive proportionally greater resources

---

## 🌐 Live Dashboard

Streamlit Community Cloud deployment:

🔗 **https://adf-myx-gp-structural-disadvantage.streamlit.app/**
🔗 **https://adf-myx-gp-spatial-scatter.streamlit.app/**

---

## 📂 Repository Structure

```
project-root/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── final_project.qmd
├── final_project.html
├── final_project.pdf
│
├── data/
│   ├── raw-data/
│   │   ├── cps_info.csv
│   │   ├── 5essentials.xlsx
│   │   ├── spaceuse.xlsx
│   │   ├── demo_lepiepfrm.xlsx
│   │   ├── demo_racialethnic.xlsx
│   │   ├── iar_proficiency.csv
│   │   └── community_boundaries.csv
│   │
│   └── derived-data/
│       ├── cps_df.csv
│       ├── plot_RI_vs_OI.png
│       └── plot_spatial_distribution.png
│
├── code/
│   ├── preprocessing.qmd
│   ├── plot_RI_vs_OI.qmd
│   └── plot_spatial_distribution.qmd
│
└── streamlit-app/
    ├── plot_app_structural_disadvantage.py
    └── plot_app_spatial_scatter.py
```

---

## 📊 Data Sources

### School Profile Data
Chicago Public Schools School Profile Information  
https://data.cityofchicago.org/Education/Chicago-Public-Schools-School-Profile-Information-/9a5f-2r4p/about_data  

### Space Utilization (Facilities)
CPS Facility Standards  
https://www.cps.edu/services-and-supports/school-facilities/facility-standards  

### Academic Performance
Illinois Assessment of Readiness (IAR) Reports  
https://www.cps.edu/about/district-data/metrics/assessment-reports/  

### Student Demographics
English Learners / Disabilities / Economic Disadvantage  
https://www.cps.edu/about/district-data/demographics/  

Racial/Ethnic Composition  
https://www.cps.edu/about/district-data/demographics/  

### Institutional Quality (5Essentials)
Obtained via professional outreach to a mentor at the Chicago Public Education Fund (internship connection).

> Note: If access is restricted in the future, users should contact CPS or the Chicago Public Education Fund.

### Community Area Boundaries
Chicago Community Boundaries  
https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-Map/cauq-8yn6  

---

## 🔧 Data Processing

All preprocessing is conducted in:

```
code/preprocessing.qmd
```

### Workflow:

1. Load raw datasets from `data/raw-data/`
2. Standardize School IDs
3. Merge institutional, demographic, geographic, and test datasets
4. Construct indices:
   - Hard Resource Index
   - Soft Resource Index
   - Resource Index (RI)
   - Opportunity Index (OI)
5. Output cleaned dataset to:

```
data/derived-data/cps_df.csv
```

---

## 🧪 Methodology

### Resource Index (RI)

**Hard Resources**
- Adjusted Space Utilization
- Nonlinear crowding penalty centered at efficiency level

**Soft Resources**
- Ambitious Instruction
- Effective Leaders
- Collaborative Teachers
- Involved Families
- Supportive Environment

All components standardized (z-scores):

$begin:math:display$
RI \= 0\.5\(Hard\) \+ 0\.5\(Soft\)
$end:math:display$

---

### Opportunity Index (OI)

Captures cumulative disadvantage exposure:

- % Economically Disadvantaged
- % English Learners
- % Students with Disabilities
- Simpson Diversity Concentration Index

Standardized and averaged:

$begin:math:display$
OI \= \(Z\_\{ED\} \+ Z\_\{ELL\} \+ Z\_\{DIS\} \+ Z\_\{RACE\}\) \/ 4
$end:math:display$

Higher OI = greater structural disadvantage.

---

## 📈 Analysis

We estimate:

$begin:math:display$
RI \= \\alpha \+ \\beta OI \+ \\varepsilon
$end:math:display$

Using OLS regression.

Outputs:
- Scatter plot with regression line
- p-value
- Slope coefficient
- Community-level spatial distribution maps

---

## 🚀 Running the Project

### Install dependencies

```
pip install -r requirements.txt
```

---

### Run preprocessing

```
python code/preprocessing.py
```

---

### Launch Streamlit App

```
streamlit run streamlit-app/app.py
```

---

## 📌 Key Findings

- Resource allocation is not uniformly aligned with structural disadvantage.
- There exists a statistically significant relationship between OI and academic performance.
- High-need schools are spatially clustered in specific Chicago communities.
- Current allocation mechanisms may not fully offset structural inequality.

---

## 👥 Authors

Andi Fang (andifang@uchicago.edu) 
University of Chicago — Harris School of Public Policy  

Minyang Xu (minyangx@uchicago.edu) 
University of Chicago — Harris School of Public Policy  

---

## 📜 License

This repository is for academic use as part of a graduate course project.