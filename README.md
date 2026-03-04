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

Let:

- $U_i$ = space utilization rate of school $i$  
- $c = 0.85$ = efficiency center

We apply a nonlinear crowding penalty centered at the optimal utilization level:

$$
Hard_i = - (U_i - c)^2
$$

This specification assigns the highest value to schools operating near the efficiency center and penalizes both overcrowding and underutilization.

The measure is then standardized:

$$
Hard_i^{*} = \frac{Hard_i - \mu_{Hard}}{\sigma_{Hard}}
$$

---

**Soft Resources**

Soft resources are derived from the five 5Essentials dimensions:

- Ambitious Instruction (AI)
- Effective Leaders (EL)
- Collaborative Teachers (CT)
- Involved Families (IF)
- Supportive Environment (SE)

Each component is standardized (z-score), and the composite score is computed as:

$$
Soft_i = \frac{
Z_{AI,i} +
Z_{EL,i} +
Z_{CT,i} +
Z_{IF,i} +
Z_{SE,i}
}{5}
$$

---

**Final Resource Index**

All components are standardized before aggregation:

$$
RI_i = 0.5 \cdot Hard_i^{*} + 0.5 \cdot Soft_i
$$

---

### Opportunity Index (OI)

Captures cumulative disadvantage exposure:

- % Economically Disadvantaged
- % English Learners
- % Students with Disabilities
- Simpson Diversity Concentration Index

Standardized and averaged:

$$
OI = \frac{Z_{ED} + Z_{ELL} + Z_{DIS} + Z_{RACE}}{4}
$$

Higher OI indicates greater structural disadvantage.

---

## 🚀 Running the Project

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Data Preprocessing

All raw data are located in:

```
data/raw-data/
```

To clean and merge datasets, run:

```bash
python code/preprocessing.py
```

This will generate:

```
data/derived-data/cps_df.csv
```

---

### 3️⃣ Reproduce Analysis Figures (Quarto)

The analytical visualizations are written in Quarto:

- `code/analysis/plot_RI_vs_OI.qmd`
- `code/analysis/plot_spatial_distribution.qmd`

To render them:

```bash
quarto render code/analysis/plot_RI_vs_OI.qmd
quarto render code/analysis/plot_spatial_distribution.qmd
```

This will generate corresponding PDF outputs.

---

### 4️⃣ Launch Streamlit Application

The interactive dashboard is located in:

```
streamlit-app/app.py
```

It imports visualization modules from:

```
code/streamlit_components/
    ├── plot_app_structural_disadvantage.py
    └── plot_app_spatial_scatter.py
```

To run locally:

```bash
streamlit run streamlit-app/app.py
```

---

### 5️⃣ Full Reproduction Order

For a complete rebuild from scratch:

```bash
pip install -r requirements.txt
python code/preprocessing.py
quarto render code/analysis/plot_RI_vs_OI.qmd
quarto render code/analysis/plot_spatial_distribution.qmd
streamlit run streamlit-app/app.py
```

---

## 👥 Authors

Andi Fang (andifang@uchicago.edu) 
University of Chicago — Harris School of Public Policy  

Minyang Xu (minyangx@uchicago.edu) 
University of Chicago — Harris School of Public Policy  

---

## 📜 License

This repository is for academic use as part of a graduate course project.