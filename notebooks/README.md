# Notebooks overview

This directory contains Jupyter notebooks used to **understand, implement,
and validate** the Horvath DNA methylation age (DNAmAge) model.

The notebooks are organized to reflect a clear workflow:
data preprocessing → model implementation → validation.

These notebooks are intended for **transparency, documentation, and
step-by-step understanding**.  
The final automated workflow is implemented separately in the pipeline
under `src/mclock/`.

---

## Notebook workflow

Recommended execution order:

1. `01_preprocess_GSE40279.ipynb`
2. `02_horvath_python.ipynb`
3. `03_compare_with_agep.ipynb`

---

## 01_preprocess_GSE40279.ipynb

**Purpose:**  
Preprocess the raw GEO dataset **GSE40279** and generate clean input files
for downstream analysis.

**What this notebook does:**
- inspects the structure of the raw GEO series matrix
- extracts the CpG × Sample DNA methylation β-value matrix
- extracts sample metadata (age, gender) from GEO GSM records
- performs basic consistency checks
- exports processed data to `data/processed/`

**Output files:**
- `GSE40279_beta_for_R.csv`
- `GSE40279_sample_metadata.csv`

This notebook focuses on **data understanding and preprocessing**.
Exploratory code used to inspect the raw file structure is preserved
in an appendix section.

---

## 02_horvath_python.ipynb

**Purpose:**  
Implement the Horvath DNAmAge model **explicitly in Python**.

**What this notebook does:**
- loads the processed β-value matrix
- loads Horvath CpG coefficients extracted from the R implementation
- computes the linear predictor of DNAmAge
- applies the original inverse age transformation (`invF`)
- exports Python-based DNAmAge predictions

**Key points:**
- No model training is performed
- CpG selection and coefficients follow the original Horvath model
- The inverse transformation step is explicitly implemented in Python

**Output file:**
- `GSE40279_DNAmAge_python.csv`

This notebook demonstrates a **faithful Python reproduction**
of the Horvath DNAmAge model.

---

## 03_compare_with_agep.ipynb

**Purpose:**  
Validate the Python implementation against the reference R implementation
(`wateRmelon::agep`).

**What this notebook does:**
- loads DNAmAge predictions from Python and R
- aligns samples between the two results
- evaluates agreement using MAE, RMSE, R², and bias
- visualizes agreement with a scatter plot

**Key outcome:**
- The Python implementation closely reproduces the R implementation,
  confirming correctness of the model implementation.

This notebook serves as the **final validation step** in the workflow.

---

## Relation to the automated pipeline

While these notebooks document the development and validation process,
the **production-ready workflow** is implemented in the automated pipeline: