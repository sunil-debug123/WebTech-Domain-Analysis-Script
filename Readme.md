- **WebTech Domain Analysis Script**

    This script is designed to analyze a list of domains using the WebTech tool and export the results to a CSV file. 
    It utilizes the WebTech library to detect technologies used by the given domains and 
    extracts the detected technologies into a structured format.

**- Usage**
Ensure you have Python installed on your system. This script requires Python 3.

- Install the required dependencies using pip:
    - pip install -r requirements.txt
    - Create a file containing a list of domains (one domain per line) that you want to analyze. 
    Place the file in Name in Script or specify a different input file when running the script.

**- Run the script:**
    * python3 main.py
    * Optionally, you can specify the input file, output file, and start index:
    * python webtech_analysis.py <input_file> <output_file> <start_index>
        - input_file: Path to the file containing the list of domains to analyze.
        - output_file: Path to the CSV file where the results will be exported.
        - start_index: Index to start processing domains from the input file.
    * The script will output logging messages indicating the progress and any errors encountered during the analysis process.

**- Dependencies**
    * webtech: A Python library for detecting technologies used by websites.
    * csv: Python's built-in module for CSV file operations.
    * logging: Python's built-in module for logging.
    * time: Python's built-in module for handling time-related functions.

**- Notes**
    If any connection errors occur during the analysis, the script will retry up to 3 times 
    with a delay of 5 seconds between retries.
    Detected technologies for each domain are extracted and exported to a CSV file with columns: Serial Number, Domain, and Technology Stack.










