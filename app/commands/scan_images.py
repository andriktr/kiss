import subprocess
import json
import click
import shutil
from tabulate import tabulate
from app.utils.other_utils import parse_namespaces, configure_logging, parse_vulnerabilities, display_basic_vulnerability_table_summary, parse_vulnerabilities_full, display_full_vulnerability_table_summary
from app.utils.trivy_utils import run_trivy_scan, run_trivy_scans_in_parallel, trivy_db_update, look_for_trivy
from app.options.cli_options import (
    namespace_option,
    selector_option,
    all_namespaces_option,
    log_level_option,
    kubeconfig,
    scan_level_option,
    severity_option,
    ignore_unfixed_option,
    pkg_types_option,
    scanners_option,
    parallel_images_option,
    parallel_namespaces_option,
    sort_by_severity_option,
    show_vulnerable_only_option,
)
from app.utils.kubernetes_utils import load_kube_config, get_unique_images_in_namespace
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock


# Global cache for scanned images this will help to avoid re-scanning the same image multiple times
# and speed up the process
scanned_images_cache = {}
cache_lock = Lock()

@click.command(name="scan-images")
@namespace_option()
@selector_option()
@all_namespaces_option()
@log_level_option()
@kubeconfig()
@scan_level_option()
@severity_option()
@ignore_unfixed_option()
@pkg_types_option()
@scanners_option()
@parallel_images_option()
@parallel_namespaces_option()
@sort_by_severity_option()
@show_vulnerable_only_option()


def scan_images(kubeconfig, all_namespaces, namespace, selector, log_level, scan_level, severity, ignore_unfixed, pkg_types, scanners, parallel_images, parallel_namespaces, sort_by_severity, show_vulnerable_only):
    """
    Scan container images for vulnerabilities in one or more Kubernetes namespaces.
    """
    configure_logging(log_level)
    
    if kubeconfig:
        load_kube_config(kubeconfig)
    else:
        load_kube_config()
    
    # Check if Trivy is installed
    look_for_trivy()
    
    # Update trivy db before running the scan
    trivy_db_update()
    
    # Parse namespaces using the utility function
    try:
        namespaces = parse_namespaces(all_namespaces, namespace, selector)
    except ValueError as e:
        raise click.UsageError(str(e))

    # Process namespaces in parallel
    with ThreadPoolExecutor(max_workers=parallel_namespaces) as executor:
        future_to_namespace = {
            executor.submit(process_namespace, ns, severity, ignore_unfixed, pkg_types, scanners, parallel_images, show_vulnerable_only, scan_level): ns
            for ns in namespaces
        }
        
        for future in as_completed(future_to_namespace):
            ns = future_to_namespace[future]
            try:
                namespace_summary, namespace_detailed_summary = future.result()
                if namespace_summary:
                    click.echo(f"\n\033[1;32mResults for namespace: {ns}\033[0m")
                    display_basic_vulnerability_table_summary(namespace_summary, sort_by_severity)
                if scan_level == "full" and namespace_detailed_summary:
                    click.echo(f"\n\033[1;32mDetailed results for namespace: {ns}\033[0m")
                    display_full_vulnerability_table_summary(namespace_detailed_summary, sort_by_severity)
            except Exception as e:
                click.echo(f"\033[1;31mError processing namespace {ns}: {e}\033[0m")
        # for future in as_completed(future_to_namespace):
        #     ns = future_to_namespace[future]
        #     try:
        #         namespace_summary = future.result()
        #         if not namespace_summary:
        #             continue
        #         else:                                
        #             click.echo(f"\n\033[1;32mResults for namespace: {ns}\033[0m")
        #             display_basic_vulnerability_table_summary(namespace_summary, sort_by_severity)
        #             if scan_level == "full":
        #                 click.echo(f"\n\033[1;32mDetailed results for namespace: {ns}\033[0m")
        #                 display_full_vulnerability_table_summary(namespace_detailed_summary, sort_by_severity)
        #     except Exception as e:
        #         click.echo(f"\033[1;31mError processing namespace {ns}: {e}\033[0m")

def process_namespace(namespace, severity, ignore_unfixed, pkg_types, scanners, parallel_images, show_vulnerable_only, scan_level):
    """
    Process a single namespace: get images, run Trivy scans, and parse vulnerabilities.

    Args:
        namespace (str): The namespace to process.
        severity (str): Comma-separated severity levels.
        ignore_unfixed (bool): Whether to include unfixed vulnerabilities.
        pkg_types (str): Comma-separated package types to scan.
        scanners (str): Comma-separated scanners to use.
        parallel_images (int): Number of images to scan in parallel.
        show_vulnerable_only (bool): Whether to show only vulnerable images.
        scan_level (str, optional): Scan level, e.g., "full" for detailed summary.

    Returns:
        tuple: (namespace_summary, namespace_detailed_summary or None)
    """
    images = get_unique_images_in_namespace(namespace)

    # Prepare a list of images to scan, skipping already scanned ones
    images_to_scan = []
    for image in images:
        with cache_lock:
            if image not in scanned_images_cache:
                images_to_scan.append(image)

    # Run Trivy scans for all new images in the namespace
    scan_results = run_trivy_scans_in_parallel(images_to_scan, severity, ignore_unfixed, pkg_types, scanners, parallel_images)

    # Update the cache with the new scan results
    with cache_lock:
        for image, result in scan_results.items():
            scanned_images_cache[image] = result

    # Parse vulnerabilities and prepare summaries
    namespace_summary = []
    namespace_detailed_summary = [] if scan_level == "full" else None
    for image in images:
        with cache_lock:
            trivy_output = scanned_images_cache.get(image)
        if trivy_output:
            namespace_summary.extend(parse_vulnerabilities(image, trivy_output, show_vulnerable_only))
            if scan_level == "full":
                namespace_detailed_summary.extend(parse_vulnerabilities_full(image, trivy_output, show_vulnerable_only))
    return namespace_summary, namespace_detailed_summary