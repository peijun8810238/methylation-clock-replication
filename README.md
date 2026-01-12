# Methylation Clock Replication Pipeline (Horvath DNAmAge)

This document describes the **end-to-end pipeline design** for replicating the  
Horvath DNA methylation age (DNAmAge) using public GEO data.

---

## Purpose

The goal of this pipeline is to:

- Reproduce the Horvath DNAmAge model in **Python**
- Validate results against the canonical **R implementation (`agep()` from wateRmelon)**
- Provide a **fully automated, config-driven workflow** suitable for research and client work

---

## Pipeline Overview

The workflow consists of two main stages:

1. **Prepare stage**: raw GEO data → processed inputs  
2. **Pipeline stage**: DNAmAge prediction → validation and visualization  

Each stage can be executed independently.

---

## Stage 1: Prepare (raw → processed)

### Description

The prepare stage generates all intermediate files required by the main pipeline.

This includes:

- β-value matrix derived from GEO series matrix files
- Sample metadata (chronological age, sex)
- Horvath model coefficients extracted at runtime from R
- DNAmAge estimates computed using R `agep()`

### Command

```bash
pip install -e . 
python scripts/prepare_inputs.py
```

Optional flags:

```bash
--force           # re-generate outputs even if files exist
--skip-metadata   # skip GEO metadata extraction
--skip-r          # skip R-based steps (coefficients / agep)
```

### Outputs

```text
data/processed/
├── GSE40279_beta_for_R.csv
├── GSE40279_sample_metadata.csv
├── horvath_coefficients_from_runtime.csv
└── GSE40279_DNAmAge_agep.csv
```

---

## Stage 2: Pipeline (prediction + validation)

### Description

This stage performs the following steps:

- Load processed inputs
- Compute DNAmAge in Python using Horvath coefficients
- Compare Python results against R `agep()` output
- Generate summary metrics and figures

### Command

```bash
pip install -e . 
python run_pipeline.py
```

### Outputs

- DNAmAge comparison table
- Summary metrics (MAE, correlation)
- Scatter plot comparing Python vs R predictions

---

## Project Structure (Relevant Parts)

```text
src/mclock/
├── pipeline.py        # main DNAmAge prediction pipeline
├── prepare.py         # prepare-stage orchestration
├── config.py          # config parsing and validation
├── logger.py          # centralized logging setup
├── rutils.py          # R script execution helpers
└── io/
    ├── files.py       # CSV / filesystem I/O
    └── geo.py         # GEO-specific parsing utilities
```

---

## Configuration Design

All paths and parameters are defined in a YAML config file:

```text
config/default.yaml
```

Design principles:

- No hardcoded paths in code
- All I/O locations configurable
- Safe defaults with explicit overrides

---

## Reproducibility Principles

- Large data files are **not tracked by Git**
- All results are reproducible from public GEO data
- R and Python steps are logged with timestamps
- Each stage can be re-run independently

---

## Intended Use Cases

This pipeline is suitable for:

- Epigenetic clock replication studies
- DNA methylation analysis on GEO / TCGA datasets
- Python–R interoperability demonstrations
- Client-facing, reproducible bioinformatics workflows

---

## Notes

- The Horvath model coefficients are **not hardcoded** and are extracted dynamically from R
- Python implementation strictly mirrors the published model application
- This pipeline focuses on **model application**, not re-training

---

## References

- Horvath S. (2013). *DNA methylation age of human tissues and cell types*
- GEO accession: **GSE40279**
---

# 日本語解説（Japanese）

このドキュメントは、Horvath の **DNAメチル化年齢（DNAmAge）** を再現するための  
**自動化パイプラインの設計・実行手順**をまとめたものです。

---

## 目的

- Horvath DNAmAge を **Python で忠実に計算**できるようにする  
- R（wateRmelon の `agep()`）の結果と **整合性を確認**する  
- 設定ファイル駆動（ハードコーディング無し）で、**研究・業務でも再利用できる**形にする  

---

## パイプライン全体像

本ワークフローは 2 つのステージから成ります。

1. **Prepare ステージ**（raw → processed）  
   公開 GEO データから、推定・検証に必要な入力ファイルを生成します。

2. **Pipeline ステージ**（prediction + validation）  
   Python で DNAmAge を推定し、R `agep()` の結果と比較して指標・図を出力します。

各ステージは独立に実行できます。

---

## Stage 1: Prepare（raw → processed）

### 何をするか

- GEO series matrix から **β値行列（CpG × サンプル）** を作成  
- GEO から **サンプルメタデータ（年齢・性別など）** を抽出  
- R 実行時に Horvath の係数を取得し、CSV として保存  
- R `agep()` を実行し、DNAmAge を CSV 出力  

### 実行例

```bash
pip install -e . 
python scripts/prepare_inputs.py
```

オプション例：

```bash
--force           # 既存ファイルがあっても再生成
--skip-metadata   # GEO metadata 抽出をスキップ
--skip-r          # R ステップ（係数 / agep）をスキップ
```

### 生成物（例）

```text
data/processed/
├── GSE40279_beta_for_R.csv
├── GSE40279_sample_metadata.csv
├── horvath_coefficients_from_runtime.csv
└── GSE40279_DNAmAge_agep.csv
```

---

## Stage 2: Pipeline（推定・検証）

### 何をするか

- processed 入力を読み込み  
- Horvath 係数を使って **Python で DNAmAge を計算**  
- R `agep()` の DNAmAge と **比較（MAE / 相関など）**  
- **散布図**を出力  

### 実行例

```bash
pip install -e . 
python run_pipeline.py
```

---

## 再現性・運用の考え方

- `data/raw/` と `data/processed/` は **GitHub で追跡しない**（大容量のため）  
- すべての出力は **公開データから再生成可能**  
- 重要な I/O や R 実行ログは **ログファイルに記録**される  

---

## 想定ユースケース

- エピジェネティッククロックの再現・検証  
- GEO/TCGA などのメチル化データの前処理と推定パイプライン  
- Python ↔ R の再現可能な連携例（ポートフォリオ / 業務設計）  

