import logging
import sys
from tabulate import tabulate

from app.utils.kubernetes_utils import get_all_namespaces_names, get_all_namespaces_names, get_namespace_names_based_on_label_selector

def configure_logging(log_level):
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%d/%m/%Y %I:%M:%S %p",
    )

def parse_namespaces(all_namespaces, namespace, selector):
    """
    Determine which namespaces to process based on the provided arguments.

    Args:
        all_namespaces (bool): Whether to process all namespaces.
        namespace (tuple): Specific namespaces provided by the user.
        selector (str): Label selector to filter namespaces.

    Returns:
        list: A list of namespaces to process.
    """
    if all_namespaces:
        namespaces = get_all_namespaces_names()
    else:
        # Validate that --namespace and --selector are not used together
        if namespace and selector:
            raise ValueError("You cannot specify both --namespace and --selector at the same time.")
        if namespace:
            # If --namespace is provided, process the specified namespaces
            namespaces = namespace
        elif selector:
            # If --selector is provided, filter namespaces by the label selector
            namespaces = get_namespace_names_based_on_label_selector(selector)
        else:
            # Default behavior if no arguments are provided
            default_namespace = "default"
            namespaces = [default_namespace]
            print(f"\033[93mNo namespace or selector specified. Using default namespace: {default_namespace}\033[0m")
    return namespaces

def image_list_table_output(namespace, images):
    """
    Format a list of images for output.

    Args:
        images (list): List of image names.
        namespace (str): Namespace to which the images belong.

    Returns:
        None: Prints the formatted table.
    """
    # Prepare table data
    table_data = [[i + 1, image] for i, image in enumerate(images)]
    table_headers = ["#", "Image"]
    # Print table output
    print(tabulate(table_data, headers=table_headers, tablefmt="fancy_grid", showindex=False))   

def parse_vulnerabilities(image_name, trivy_output, show_vulnerable_only=False):
    """
    Parse the Trivy JSON output to count vulnerabilities by severity.

    Args:
        image_name (str): Name of the image being analyzed.
        trivy_output (dict): JSON output from Trivy.
        show_vulnerable_only (bool): Whether to include only images with vulnerabilities.

    Returns:
        list: A list of vulnerability summaries for the image.
    """
    results = []
    if not trivy_output or "Results" not in trivy_output:
        return results

    for result in trivy_output["Results"]:
        vulnerabilities = result.get("Vulnerabilities", [])

        # Count vulnerabilities by severity
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
        for vuln in vulnerabilities:
            severity = vuln.get("Severity", "").upper()
            if severity in severity_counts:
                severity_counts[severity] += 1

        # Check if the image has vulnerabilities
        if not show_vulnerable_only or any(severity_counts.values()):
            results.append(
                [
                    image_name,
                    severity_counts["CRITICAL"],
                    severity_counts["HIGH"],
                    severity_counts["MEDIUM"],
                    severity_counts["LOW"],
                    severity_counts["UNKNOWN"],
                ]
            )

    return results
  
def sort_by_severity_type(table_data):
    """
    Sort the vulnerability summary by severity type.
    First namespaces with the highest severity count are shown.
    """
    # Sort the summary by severity counts in descending order
    sorted_summary = sorted(
        table_data,
        key=lambda x: (
            x[2],  # Critical
            x[3],  # High
            x[4],  # Medium
            x[5],  # Low
            x[6],  # Unknown
        ),
        reverse=True,
    )
    return sorted_summary

def display_basic_vulnerability_table_summary(summary, sort_by_severity):
    """
    Display the vulnerability summary as a table.
    """
    headers = [
        "#",
        "Image",
        "\033[1;31mCritical\033[0m",  # Red
        "\033[1;33mHigh\033[0m",      # Bold Yellow (distinct from Critical)
        "\033[1;93mMedium\033[0m",    # Bright Yellow
        "\033[1;34mLow\033[0m",       # Blue
        "\033[1;35mUnknown\033[0m",   # Magenta
    ] 
    table_data = [[i + 1] + row for i, row in enumerate(summary)]
    if sort_by_severity:
        sorted_summary = sort_by_severity_type(table_data)
        # reindex the sorted summary
        sorted_summary = [[i + 1] + row[1:] for i, row in enumerate(sorted_summary)]
        print(tabulate(sorted_summary, headers=headers, tablefmt="fancy_grid", showindex=False))
    else:
        summary = table_data
        print(tabulate(summary, headers=headers, tablefmt="fancy_grid", showindex=False))

def parse_vulnerabilities_full(image_name, trivy_output, show_vulnerable_only=False):
    """
    Parse the Trivy JSON output to extract detailed vulnerability information.

    Args:
        image_name (str): Name of the image being analyzed.
        trivy_output (dict): JSON output from Trivy.

    Returns:
        list: A list of detailed vulnerability information for the image.
    """
    results = []
    if not trivy_output or "Results" not in trivy_output:
        return results

    for result in trivy_output["Results"]:
        vulnerabilities = result.get("Vulnerabilities", [])
        for vuln in vulnerabilities:
            severity = vuln.get("Severity", "").upper()
            if not show_vulnerable_only or severity != "UNKNOWN":
                results.append(
                    [
                        image_name,
                        severity,
                        vuln.get("VulnerabilityID", ""),
                        vuln.get("PkgName", ""),
                        vuln.get("InstalledVersion", ""),
                        vuln.get("FixedVersion", ""),
                        vuln.get("PrimaryURL", ""),
                    ]
                )
    return results

def sort_by_severity_type_full(table_data):
    """
    Sort the detailed vulnerability summary by severity type, with CRITICAL first,
    then HIGH, MEDIUM, LOW, UNKNOWN, and then by other columns.
    """
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}
    sorted_summary = sorted(
        table_data,
        key=lambda x: (
            severity_order.get(x[2], 99),  # x[2] is Severity
            x[3],  # Vulnerability ID
            x[4],  # Package Name
            x[5],  # Installed Version
            x[6],  # Fixed Version
        )
    )
    return sorted_summary

def display_full_vulnerability_table_summary(summary, sort_by_severity):
    """
    Display the detailed vulnerability summary as a table.
    """
    headers = [
        "#",
        "Image",
        "Severity",
        "Vulnerability ID",
        "Package Name",
        "Installed Version",
        "Fixed Version",
        "Primary URL",
    ]
    table_data = [[i + 1] + row for i, row in enumerate(summary)]
    if sort_by_severity:
        sorted_summary = sort_by_severity_type_full(table_data)
        # reindex the sorted summary
        sorted_summary = [[i + 1] + row[1:] for i, row in enumerate(sorted_summary)]
        print(tabulate(sorted_summary, headers=headers, tablefmt="fancy_grid", showindex=False))
    else:
        summary = table_data
        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid", showindex=False))
