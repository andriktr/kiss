import click

def namespace_option():
    return click.option(
        "--namespace",
        "-n",
        multiple=True,
        help=("Specify one or more namespaces to process."
              "Can be specified multiple times i.e. -n ns1 -n ns2."
              "If not specified, the default namespace will be used."           
        ),      
    )

def selector_option():
    return click.option(
        "--selector",
        "-l",
        help=("Filter namespaces by a label selector (e.g., -l app=my-app)."             
        ),
    )

def all_namespaces_option():
    return click.option(
        "--all-namespaces",
        "-A",
        is_flag=True,
        help=(
            "Process all namespaces. Overrides --namespace and --selector if provided."            
        )
    )

def log_level_option():
    return click.option(
        "--log-level",
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
        default="INFO",
        help=("Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)."       
        ),
    )

def kubeconfig():
    return click.option(
        "--kubeconfig",
        default=None,
        help=("Path to the kubeconfig file. If not specified, the default kubeconfig file will be used."     
        ),
    )
    
def scan_level_option():
    return click.option(
        "--scan-level",
        type=click.Choice(["basic", "full"], case_sensitive=False),
        default="basic",
        help=("Set the scan level (basic or full)."           
        ),
    )
    
def severity_option():
    return click.option(
        "--severity",
        type=click.Choice(["UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"], case_sensitive=True),
        multiple=True,
        help=(
            "Set the severity levels for filtering results"
            "Can be specified multiple times i.e. --severity HIGH --severity CRITICAL."
            "If not specified, all severity levels will be included."
        ),
    )

def ignore_unfixed_option():
    return click.option(
        "--ignore-unfixed",
        is_flag=True,
        default=True,
        help=("Ignore unfixed vulnerabilities in the scan results."
        ),
    )

def pkg_types_option():
    return click.option(
        "--pkg-types",
        type=click.Choice(["os", "library"], case_sensitive=False),
        multiple=True,
        default=["os"],
        help=(
            "Specify list of package types (os,library) (default [os])."
            "Can be specified multiple times i.e. --pkg-types os --pkg-types library."
            "If not specified, os will be used."
        )
    )

def scanners_option():
    return click.option(
        "--scanners",
        type=click.Choice(["vuln", "secret", "license", "misconfig"], case_sensitive=False),
        multiple=True,
        default=["vuln"],
        help=(
            "Security issues to detect (vuln,misconfig,secret,license) (default [vuln])."
            "If not specified, vuln will be used."
            "Can be specified multiple times i.e. --scanners vuln --scanners secret."
        )
    )

def parallel_images_option():
    return click.option(
        "--parallel-images",
        type=int,
        default=20,
        help=(
            "Number of images to scan in parallel."
            "Be careful with this option as it can consume additional compute resources."
        )             
    )

def parallel_namespaces_option():
    return click.option(
        "--parallel-namespaces",
        type=int,
        default=5,
        help=(
            "Number of namespaces to process in parallel."
            "Be careful with this option as it can consume additional compute resources."
        )
    )

def sort_by_severity_option():
    return click.option(
        "--sort-by-severity",
        is_flag=True,
        default=False,
        help=(
            "Sort the output by severity level."
            "If not specified, the output will not be sorted."
            "If specified, the output will be sorted by severity level with the highest severity first."
        )
    )

def show_vulnerable_only_option():
    return click.option(
        "--show-vulnerable-only",
        is_flag=True,
        default=False,
        help=(
            "Show only images with vulnerabilities."
            "If not specified, all images will be shown."
        )
    )
