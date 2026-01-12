Horvath DNAmAge Replication Pipeline

A reproducible Python implementation and validation of the Horvath DNA methylation age clock.

⸻

Overview

This repository provides a fully reproducible implementation of the Horvath
DNA methylation age (DNAmAge) model, using publicly available DNA methylation
array data from GEO (GSE40279).

The project is designed to clearly separate:
	•	exploratory analysis and understanding (Jupyter notebooks)
	•	production-ready, automated analysis (Python pipeline)

The Python implementation is carefully validated against the reference
R implementation (wateRmelon::agep) to ensure correctness.

⸻

Project structure

.
├── data/
│   ├── raw/                # Raw GEO data (GSE40279)
│   ├── processed/          # Processed β matrices, metadata, predictions
│   └── external/           # External reference files
├── notebooks/              # Exploratory and validation notebooks
│   ├── 01_preprocess_GSE40279.ipynb
│   ├── 02_horvath_python.ipynb
│   ├── 03_compare_with_agep.ipynb
│   └── README.md
├── src/
│   └── mclock/             # Automated DNAmAge pipeline
├── config/
│   └── default.yaml        # Pipeline configuration
├── run_pipeline.py         # Pipeline entry point
├── pyproject.toml
└── README.md


⸻

Notebook workflow

The notebooks document the full reasoning process behind the pipeline and are
intended for transparency and step-by-step understanding.

Recommended execution order:
	1.	01_preprocess_GSE40279.ipynb
Inspect the raw GEO series matrix, construct a CpG × Sample β-value matrix,
extract sample metadata (age, gender), and export processed data.
	2.	02_horvath_python.ipynb
Implement the Horvath DNAmAge model explicitly in Python, including
the original inverse age transformation (invF).
	3.	03_compare_with_agep.ipynb
Validate the Python implementation against the reference R implementation
(wateRmelon::agep) using quantitative metrics and visual inspection.

For detailed descriptions, see notebooks/README.md.

⸻

Automated pipeline

After validation in the notebooks, the same logic is implemented as an
automated, configuration-driven pipeline under src/mclock/.

Pipeline features:
	•	configuration-based execution (no hard-coded paths)
	•	reproducible DNAmAge prediction
	•	comparison with reference results
	•	structured logging and automatic figure generation

Example usage

pip install -e .
python run_pipeline.py --config config/default.yaml


Prepare stage (raw → processed)

Before running the main pipeline, generate the required processed inputs (β matrix, sample metadata, reference predictions, and coefficient table). This stage is implemented in scripts/prepare_inputs.py and writes outputs to the paths specified in config/default.yaml (paths.*).

What it produces (typical)
- data/processed/GSE40279_beta_for_R.csv (β-value matrix; CpGs × samples)
- data/processed/GSE40279_sample_metadata.csv (age / gender extracted from GEO metadata)
- data/processed/horvath_coefficients_from_runtime.csv (Horvath coefficients exported from wateRmelon at runtime)
- data/processed/GSE40279_DNAmAge_agep.csv (reference DNAmAge from wateRmelon::agep)

Dependencies
- Python (optional): GEOparse (required only for metadata extraction)
  - pip install GEOparse
- R (required for reference outputs): Rscript available in PATH
  - R packages: wateRmelon (Bioconductor), and its dependencies
    (If you already ran agep() successfully in your R environment, you are good.)

Run (prepare)

pip install -e .
python scripts/prepare_inputs.py --config config/default.yaml

Useful flags
- --force          Recompute outputs even if target files already exist
- --skip-metadata  Skip GEO metadata extraction (no GEOparse needed)
- --skip-r         Skip R steps (no coefficients / agep reference will be generated)

Notes on large files
Some processed files (especially β matrices) can be very large. In most cases you should not commit data/processed outputs to GitHub. Keep them local, add them to .gitignore, or use Git LFS if you must version large artifacts.


⸻

Reproducibility details
	•	Raw data source: GEO accession GSE40279
	•	DNAmAge model: Horvath (2013)
	•	Reference implementation: wateRmelon::agep
	•	Python implementation explicitly includes:
	•	CpG alignment
	•	linear predictor computation
	•	original inverse age transformation (invF)

⸻

About this work / Availability for collaboration

This repository demonstrates a transparent and auditable reproduction of a
published epigenetic clock, with emphasis on:
	•	epigenomics and DNA methylation analysis
	•	cross-language reproducibility (R ↔ Python)
	•	maintainable, well-documented analysis pipelines
	•	clear separation of exploratory and production code

I am available for collaboration or consulting work related to:
	•	DNA methylation clocks and epigenetic biomarkers
	•	methylation array / NGS data analysis
	•	reproduction and validation of published bioinformatics methods
	•	Python/R-based analysis pipeline development

If you are interested in collaboration or project-based work,
please feel free to reach out.

⸻

⸻

本リポジトリについて（日本語）

本リポジトリは、Horvath DNAメチル化年齢（DNAmAge）モデルを
Python で再現・検証することを目的とした解析・実装例です。

GEO 公開データ（GSE40279）を用い、
	•	生データ構造の理解と前処理
	•	Horvath 論文に基づく DNAmAge モデルの明示的実装
	•	R 実装（wateRmelon::agep）との定量的・視覚的検証
	•	notebook と自動化パイプラインの分離設計

を通じて、再現性と可読性を重視した解析フローを示しています。

⸻

想定する活用・対応可能な内容

本プロジェクトは、以下のような業務・研究テーマを想定した
ポートフォリオでもあります。
	•	DNAメチル化クロック・エピゲノム指標の解析
	•	メチル化アレイ／NGS データの前処理・解析
	•	既存論文手法（主に R 実装）の Python 化・再現検証
	•	再現性・保守性を重視した解析パイプラインの設計・実装

これらに関連する 共同研究・技術支援・業務委託 等のご相談がありましたら、
お気軽にご連絡ください。

⸻

License

This project is intended for research and educational purposes.
Please check the original data source and software licenses when using
this repository for downstream applications.