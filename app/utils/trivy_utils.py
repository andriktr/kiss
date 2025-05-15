import json
import subprocess
import click
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_trivy_scan(image_name, severity, ignore_unfixed, pkg_types, scanners, parallel_images):
    """
    Run a Trivy scan on the specified image with dynamic options and return the JSON output.
    """
    try:
        # Build the Trivy command dynamically
        command = ["trivy", "image", image_name, "--format", "json", "--timeout", "30m", "--skip-db-update", "--skip-java-db-update"]
        
        # Add severity levels if specified
        # Add severity levels if specified
        if severity:
            command.extend(["--severity", ",".join(severity)])  # Convert tuple to comma-separated string
        
        # Add the ignore-unfixed flag if specified
        if ignore_unfixed:
            command.append("--ignore-unfixed")
        
        # Add package types if specified
        if pkg_types:
            command.extend(["--pkg-types", ",".join(pkg_types)])  # Convert tuple to comma-separated string
        
        # Add scanners if specified
        if scanners:
            command.extend(["--scanners", ",".join(scanners)])  # Convert tuple to comma-separated string
        
        if parallel_images:
            command.extend(["--parallel", str(parallel_images)])   # Convert tuple to comma-separated string
        
        # Execute the Trivy scan as a subprocess
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        # Parse the JSON output
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running Trivy scan for image {image_name}: {e.stderr}")
        return None
    
def run_trivy_scans_in_parallel(images, severity, ignore_unfixed, pkg_types, scanners, parallel_images):
    """
    Run Trivy scans for multiple images in parallel.
    
    Args:
        images (list): List of image names to scan.
        severity (str): Comma-separated severity levels.
        ignore_unfixed (bool): Whether to include unfixed vulnerabilities.
        max_workers (int): Maximum number of parallel workers.

    Returns:
        dict: A dictionary mapping image names to their Trivy scan results.
    """
    results = {}
    with ThreadPoolExecutor(max_workers=parallel_images) as executor:
        # Submit tasks for each image
        future_to_image = {
            executor.submit(run_trivy_scan, image, severity, ignore_unfixed, pkg_types, scanners, parallel_images): image
            for image in images
        }

        # Process completed tasks
        for future in as_completed(future_to_image):
            image = future_to_image[future]
            try:
                results[image] = future.result()
            except Exception as e:
                click.echo(f"Error scanning image {image}: {e}")
                results[image] = None

    return results

def trivy_db_update(max_retries=5, delay=60):
    click.echo("Updating Trivy database...")
    attempt = 0
    while attempt < max_retries:
        try:
            subprocess.run(["trivy", "image", "--download-db-only", "--quiet"], check=True)
            click.echo("Trivy database updated successfully.")
            return
        except subprocess.CalledProcessError as e:
            attempt += 1
            logging.error(f"Error updating Trivy database (attempt {attempt}/{max_retries}): {str(e)}")
            if attempt < max_retries:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error("Max retries reached. Failed to update Trivy database.")
                return