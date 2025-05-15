import click
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.utils.other_utils import parse_namespaces, configure_logging, image_list_table_output
from app.options.cli_options import namespace_option, selector_option, all_namespaces_option, log_level_option, kubeconfig, parallel_namespaces_option
from app.utils.kubernetes_utils import load_kube_config, get_unique_images_in_namespace

@click.command(name="show-images")
@namespace_option()
@selector_option()
@all_namespaces_option()
@log_level_option()
@kubeconfig()
@parallel_namespaces_option()
def show_images(kubeconfig, all_namespaces, namespace, selector, log_level, parallel_namespaces):
    """
    Shows the unique container images in a Kubernetes namespace(-s).
    Includes images from regular containers, init containers and ephemeral containers.
    """
    configure_logging(log_level)
    
    if kubeconfig:
        load_kube_config(kubeconfig)
    else:
        load_kube_config()

    # Parse namespaces using the utility function
    try:
        namespaces = parse_namespaces(all_namespaces, namespace, selector)
    except ValueError as e:
        raise click.UsageError(str(e))

    # Process namespaces in parallel
    with ThreadPoolExecutor(max_workers=parallel_namespaces) as executor:
        future_to_namespace = {
            executor.submit(process_namespace, ns): ns
            for ns in namespaces
        }

        for future in as_completed(future_to_namespace):
            ns = future_to_namespace[future]
            try:
                images = future.result()
                click.echo(f"\n\033[1;32mResults for namespace: {ns}\033[0m")
                image_list_table_output(ns, images)
            except Exception as e:
                click.echo(f"\033[1;31mError processing namespace {ns}: {e}\033[0m")


def process_namespace(namespace):
    """
    Process a single namespace to get unique images.
    
    Args:
        namespace (str): The namespace to process.

    Returns:
        list: A list of unique images in the namespace.
    """
    return get_unique_images_in_namespace(namespace)
        