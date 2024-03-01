import csv
import logging
from webtech import WebTech
from webtech.utils import ConnectionException, WrongContentTypeException
from time import sleep

# Configure logging to display messages in the terminal and write to a file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize WebTech instance
wt = WebTech()
wt.timeout = 6  # Set a default timeout value

# Retry configuration
max_retries = 3  # Maximum number of retries for transient errors
retry_delay = 5  # Delay between retries in seconds

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

# Function to process a chunk of domains
def process_chunk(domains, start_index, csv_writer):
    results = []
    for idx, domain in enumerate(domains, start=start_index):
        domain_with_https = f"https://{domain.strip()}"
        for attempt in range(1, 4):  # Attempt up to 3 retries
            try:
                result = wt.start_from_url(domain_with_https)
                technology_stack = extract_detected_technologies(result)
                results.append({'Serial Number': idx, 'Domain': domain_with_https, 'Technology Stack': technology_stack})
                logging.info(f"Processed domain: {domain_with_https}")
                break  # Exit the loop on success
            except ConnectionException as e:
                logging.error(f"Attempt {attempt}: Connection error for domain {domain_with_https}: {e}")
                if attempt < 3:
                    sleep(5)  # Wait for 5 seconds before retrying
                else:
                    logging.error(f"Failed to process domain after 3 attempts: {domain_with_https}")
            except WrongContentTypeException as e:
                logging.error(f"Wrong content type for domain {domain_with_https}: {e}")
                break  # Skip this domain on WrongContentTypeException
    return results

# Function to export results to CSV
def export_to_csv(results, csv_writer):
    for result in results:
        csv_writer.writerow(result)

# Main function
def main(input_file, output_file, start_index, chunk_size=100):
    with open(input_file, 'r') as f:
        domains = f.readlines()

    total_domains = len(domains)
    logging.info(f"Total domains to process: {total_domains}")

    with open(f"{output_file}.csv", 'a', newline='') as csvfile:
        fieldnames = ['Serial Number', 'Domain', 'Technology Stack']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if start_index == 0:
            writer.writeheader()

        for i in range(start_index, total_domains, chunk_size):
            chunk = domains[i:i + chunk_size]
            logging.info(f"Processing chunk {i // chunk_size + 1}/{(total_domains - 1) // chunk_size + 1}")

            results = process_chunk(chunk, start_index=i + 1, csv_writer=writer)
            export_to_csv(results, csv_writer=writer)

            remaining_domains = total_domains - (i + chunk_size)
            logging.info(f"Remaining domains: {remaining_domains}")

if __name__ == "__main__":
    main("Enter the File of the Domains Here...!!", "webtech_results", start_index=0)
