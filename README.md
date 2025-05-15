# KISS (Kubernetes Image Security Scanning)

KISS your cluster with security!

This repository contains a source code of KISS application, which is a tool for scanning container images for vulnerabilities.
KISS uses Trivy as a vulnerability scanner and provides ability to scan whole namespace(-s) or entire cluster images for vulnerabilities.

Feature | Status
--- | ---
Add sort by severity | :x:
Add option to hide images with no vulnerabilities | :x:
Add option to view only images with specific severity | :x:
Add detailed reports | :x:
Add option for custom output format | :x:
Add option to scan only specific namespace | :white_check_mark:
Add option to just show running images | :white_check_mark:
Add option for parallel scanning | :white_check_mark:
Add option to scan all namespaces | :white_check_mark:
Add option select namespace by label | :white_check_mark:
Add option to select multiple namespaces | :white_check_mark: