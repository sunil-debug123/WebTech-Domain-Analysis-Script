import csv
import logging
from concurrent.futures import ThreadPoolExecutor
from webtech import WebTech
from webtech.utils import ConnectionException, WrongContentTypeException
from requests.exceptions import RequestException

# Configure logging to display messages in the terminal and write to a file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize WebTech instance
wt = WebTech()
wt.timeout = 6  # Set a default timeout value

# Function to extract detected technologies from the result
def extract_detected_technologies(result):
    tech_start = result.find("Detected technologies:")  # Finding the start of detected technologies
    if tech_start != -1:
        tech_end = result.find("Detected the following interesting custom headers:")  # Finding the end of detected technologies
        if tech_end != -1:
            technologies = result[tech_start:tech_end].strip().split("\n")[1:]  # Extracting lines containing technologies
        else:
            technologies = result[tech_start:].strip().split("\n")[1:]  # If no custom headers line found, consider till end
        technologies = [tech.strip().replace("-", "") for tech in technologies]  # Removing leading hyphen and whitespace
        return ", ".join(technologies)  # Joining technologies with comma
    return ""

# Function to process a single domain
def process_domain(serial_number, domain):
    domain_with_https = f"https://{domain.strip()}"
    try:
        result = wt.start_from_url(domain_with_https)
        technology_stack = extract_detected_technologies(result)
        logging.info(f"Processed domain: {domain_with_https}")
        return {'Serial Number': serial_number, 'Domain': domain_with_https, 'Technology Stack': technology_stack}
    except ConnectionException as e:
        logging.error(f"Connection error for domain {domain_with_https}: {e}")
    except WrongContentTypeException as e:
        logging.error(f"Wrong content type for domain {domain_with_https}: {e}")
    except RequestException as e:
        logging.error(f"Request error for domain {domain_with_https}: {e}")
    # Default return for any exception handling case
    return {'Serial Number': serial_number, 'Domain': domain_with_https, 'Technology Stack': 'Not Found'}

# Function to get the last processed domain from the CSV file
def get_last_processed_domain(csv_file):
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            last_row = None
            for row in reader:
                last_row = row
            if last_row:
                return last_row['Domain']
    except FileNotFoundError:
        # If the CSV file doesn't exist yet, return None
        pass
    return None

# Main function
def main(input_file, output_file):
    with open(input_file, 'r') as f:
        domains = f.readlines()

    total_domains = len(domains)
    logging.info(f"Total domains to process: {total_domains}")

    last_processed_domain = get_last_processed_domain(f"{output_file}.csv")
    if last_processed_domain:
        try:
            start_index = domains.index(last_processed_domain + '\n') + 1
        except ValueError:
            # If the last processed domain is not found in the input file, start from the beginning
            start_index = 0
    else:
        start_index = 0

    with open(f"{output_file}.csv", 'a', newline='') as csvfile:
        fieldnames = ['Serial Number', 'Domain', 'Technology Stack']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # If the file is empty, write the header
        if csvfile.tell() == 0:
            writer.writeheader()

        with ThreadPoolExecutor() as executor:
            results = executor.map(process_domain, range(start_index + 1, start_index + total_domains + 1), domains[start_index:])
            for result in results:
                writer.writerow(result)

    # Log a message indicating that the script has finished
    logging.info("Script finished.")

if __name__ == "__main__":
    main("Enter the File of the Domains Here...!!", "webtech_results")
