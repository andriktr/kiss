import kubernetes
import logging
from kubernetes import client, config

def load_kube_config(kubeconfig=None):
    """
    Load the Kubernetes configuration from a specified kubeconfig file or the default location.
    
    Args:
        kubeconfig (str, optional): Path to the kubeconfig file. If None, uses the default location.
    """
    if kubeconfig:
        config.load_kube_config(config_file=kubeconfig)
    else:
        config.load_kube_config()
        
def get_all_namespaces_names():
    """
    Get all namespace names in the Kubernetes cluster.
    
    Returns:
        list: List of all namespace names.
    """
    try:
        v1 = client.CoreV1Api()
        api_response = v1.list_namespace()
        namespaces = [ns.metadata.name for ns in api_response.items]
        return namespaces
    except Exception as e:
        logging.error(f"Error getting all namespace names: {e}")
        raise Exception("Error getting all namespace names") from e

        
def get_namespace_names_based_on_label_selector(*label_selectors):
    """
    Get the namespaces based on the label selectors.
    Args:
        label_selectors (str): Label selectors to filter namespaces.
    Returns:
        namespaces (list): List of namespaces that match the label selectors.
    """
    try:
        v1 = client.CoreV1Api()
        ns_set = set()
        if not label_selectors or len(label_selectors) == 0:
            api_response = v1.list_namespace()
            for ns in api_response.items:
                ns_set.add(ns.metadata.name)
        else:
            for label_selector in label_selectors:
                api_response = v1.list_namespace(label_selector=label_selector)
                for ns in api_response.items:
                    ns_set.add(ns.metadata.name)
        namespaces = sorted(list(ns_set))
        return namespaces
    except Exception as e:
        logging.error(f"Error getting namespaces based on label selectors: {e}")
        raise Exception("Error getting namespaces based on label selectors") from e

# Get unique images in the namespace
def get_unique_images_in_namespace(namespace):
    """
    Get unique container images in a namespace, including images from
    regular containers, init containers, and ephemeral containers.

    Args:
        namespace (str): The namespace to query.

    Returns:
        set: A set of unique container images.
    """
    try:
        v1 = client.CoreV1Api()
        pod_list = v1.list_namespaced_pod(namespace)
        images = set()

        for pod in pod_list.items:
            # Add images from regular containers
            if pod.spec.containers:
                for container in pod.spec.containers:
                    images.add(container.image)

            # Add images from init containers
            if pod.spec.init_containers:
                for init_container in pod.spec.init_containers:
                    images.add(init_container.image)

            # Add images from ephemeral containers
            if pod.spec.ephemeral_containers:
                for ephemeral_container in pod.spec.ephemeral_containers:
                    images.add(ephemeral_container.image)

        return images
    except Exception as e:
        logging.error(f"Error getting unique images in namespace {namespace}: {e}")
        return set()