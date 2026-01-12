#!/usr/bin/env Rscript

# ==========================================================
# Compute Horvath DNAmAge using wateRmelon::agep
# Usage:
#   Rscript scripts/run_agep_on_beta.R --beta <beta_csv> --out <agep_csv>
# ==========================================================

suppressPackageStartupMessages({
  library(wateRmelon)
})

args <- commandArgs(trailingOnly = TRUE)

# parse args: --beta <path> --out <path>
beta_path <- NULL
out_path <- NULL
for (i in seq_along(args)) {
  if (args[i] == "--beta" && i < length(args)) beta_path <- args[i + 1]
  if (args[i] == "--out"  && i < length(args)) out_path  <- args[i + 1]
}

if (is.null(beta_path) || is.null(out_path)) {
  stop("Usage: Rscript run_agep_on_beta.R --beta <beta.csv> --out <agep.csv>")
}

message(sprintf("Reading beta CSV: %s", beta_path))
beta <- read.csv(beta_path, row.names = 1, check.names = FALSE)
beta <- as.matrix(beta)
storage.mode(beta) <- "double"

message(sprintf("beta matrix dim: %d x %d", nrow(beta), ncol(beta)))

res <- agep(beta)

# --- helper to extract Horvath DNAmAge vector robustly ---
extract_age_vec <- function(res) {
  # Case 1: numeric vector
  if (is.numeric(res) && length(res) > 1) {
    return(res)
  }

  # Case 2: matrix/data.frame with a likely column
  if (is.matrix(res) || is.data.frame(res)) {
    cn <- colnames(res)
    # prefer explicit names if present
    candidates <- c("DNAmAge", "DNAmAge_agep", "Horvath", "horvath", "age", "Age")
    hit <- intersect(candidates, cn)
    if (length(hit) >= 1) {
      return(as.numeric(res[, hit[1]]))
    }
    # fallback: single column
    if (ncol(res) == 1) return(as.numeric(res[, 1]))
  }

  # Case 3: list -> search common fields
  if (is.list(res)) {
    nms <- names(res)
    message("agep() returned a list. names(res):")
    message(paste(nms, collapse = ", "))

    # try direct keys
    for (k in c("Horvath", "horvath", "DNAmAge", "age", "Age", "ages", "pred", "predicted")) {
      if (!is.null(res[[k]])) {
        v <- res[[k]]
        if (is.numeric(v)) return(as.numeric(v))
        if (is.matrix(v) || is.data.frame(v)) {
          cn <- colnames(v)
          candidates <- c("DNAmAge", "DNAmAge_agep", "Horvath", "horvath", "age", "Age")
          hit <- intersect(candidates, cn)
          if (length(hit) >= 1) return(as.numeric(v[, hit[1]]))
          if (ncol(v) == 1) return(as.numeric(v[, 1]))
        }
      }
    }

    # try any numeric element with length == ncol(beta)
    for (k in nms) {
      v <- res[[k]]
      if (is.numeric(v) && length(v) == ncol(beta)) return(as.numeric(v))
    }
  }

  return(NULL)
}

age_vec <- extract_age_vec(res)

if (is.null(age_vec)) {
  # print structure to help debugging if it fails again
  message("Unsupported agep() return format. str(res):")
  str(res)
  stop("agep() returned an unsupported format. Please inspect names(res)/str(res) above.")
}

if (length(age_vec) != ncol(beta)) {
  stop(sprintf("Extracted age vector length mismatch: got %d, expected %d", length(age_vec), ncol(beta)))
}

out_df <- data.frame(
  sample = colnames(beta),
  DNAmAge_agep = as.numeric(age_vec),
  stringsAsFactors = FALSE
)

dir.create(dirname(out_path), recursive = TRUE, showWarnings = FALSE)
write.csv(out_df, out_path, row.names = FALSE)
message(sprintf("Wrote agep results: %s", out_path))