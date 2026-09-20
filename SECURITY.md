# Security policy

## Supported versions

This is a portfolio/analytics project. Only the latest commit on `main` is
supported.

## Data

- All datasets in `data/` are **synthetic** samples created for demonstration.
  They contain no real customer information.
- No credentials, tokens or API keys are stored in the repository.
- The optional transformer model is downloaded from Hugging Face at runtime and
  cached outside the repository.

## Reporting a vulnerability

If you find a security issue (for example a leaked secret, a vulnerable
dependency, or unsafe file handling), please **do not** open a public issue.
Instead, email **pantea.mkh18@gmail.com** with:

- a description of the issue,
- the steps to reproduce it,
- any suggested fix.

You can expect an acknowledgement within a few days.
