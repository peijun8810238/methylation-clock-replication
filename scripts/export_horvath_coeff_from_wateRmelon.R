#!/usr/bin/env Rscript

# ==========================================================
# Export Horvath coefficient table used by wateRmelon::agep
# Usage:
#   Rscript scripts/export_horvath_coeff_from_wateRmelon.R --out <csv_path>
# ==========================================================

#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(wateRmelon)
})

args <- commandArgs(trailingOnly = TRUE)

# very small arg parser: expects --out <path>
out_path <- NULL
if (length(args) >= 2) {
  for (i in seq_along(args)) {
    if (args[i] == "--out" && i < length(args)) {
      out_path <- args[i + 1]
      break
    }
  }
}

if (is.null(out_path)) {
  stop("Missing --out. Example: Rscript export_horvath_coeff_from_wateRmelon.R --out data/processed/horvath_coefficients.csv")
}

try_load_data <- function(name) {
  e <- new.env(parent = emptyenv())
  ok <- tryCatch({
    data(list = name, package = "wateRmelon", envir = e)
    TRUE
  }, error = function(err) FALSE)
  if (!ok) return(NULL)
  if (!exists(name, envir = e, inherits = FALSE)) return(NULL)
  get(name, envir = e, inherits = FALSE)
}

coef_obj <- NULL

# 1) namespace objects
ns <- asNamespace("wateRmelon")
for (nm in c("ageCoefs", "coef", "coeff", "horvathCoef", "hannumCoef")) {
  if (exists(nm, envir = ns, inherits = FALSE)) {
    coef_obj <- get(nm, envir = ns, inherits = FALSE)
    message(sprintf("Found '%s' in wateRmelon namespace.", nm))
    break
  }
}

# 2) datasets
if (is.null(coef_obj)) {
  for (nm in c("ageCoefs", "coef", "coeff", "horvathCoef", "hannumCoef")) {
    obj <- try_load_data(nm)
    if (!is.null(obj)) {
      coef_obj <- obj
      message(sprintf("Loaded dataset '%s' from wateRmelon.", nm))
      break
    }
  }
}

if (is.null(coef_obj)) {
  stop("Could not find any coefficients object in wateRmelon. Tried: ageCoefs, coef, coeff, horvathCoef, hannumCoef")
}

coef_vec <- NULL
if (is.list(coef_obj)) {
  if ("Horvath" %in% names(coef_obj)) {
    coef_vec <- coef_obj[["Horvath"]]
  } else {
    idx <- which(tolower(names(coef_obj)) == "horvath")
    if (length(idx) >= 1) coef_vec <- coef_obj[[idx[1]]]
  }
} else if (is.numeric(coef_obj) && !is.null(names(coef_obj))) {
  coef_vec <- coef_obj
}

if (is.null(coef_vec) || !is.numeric(coef_vec) || is.null(names(coef_vec))) {
  stop("Found a coefficients object, but could not interpret it as Horvath named numeric vector.")
}

df <- data.frame(
  term = names(coef_vec),
  weight = as.numeric(coef_vec),
  stringsAsFactors = FALSE
)

dir.create(dirname(out_path), recursive = TRUE, showWarnings = FALSE)
write.csv(df, out_path, row.names = FALSE)

message(sprintf("Wrote coefficients: %s (n=%d)", out_path, nrow(df)))