# DataJobsScraper

## Overview
DataJobsScraper is an automated web scraping tool designed to collect job listing information specifically for Data Analytics and Data Science roles from popular job board - Career.Habr. This project aims to provide insights into the job market for IT professionals, enabling users to analyze the availability of jobs across different expertise levels (Junior, Middle, Senior), understand job requirements, and explore offered job conditions.

## Features
- **Web Scraping with Selenium**: Automates web browsers to collect job listings directly from the web pages.
- **Data Extraction**: Parses the collected HTML content to extract and organize job listing details such as job title, publication date, salary, role, qualification level, additional requirements, location, full-time/part-time status, remote availability, company name, and the job listing URL.
- **Excel Export**: Saves the extracted job listing data into an Excel file for easy analysis and sharing.
- **Configurable Searches**: Allows customization of search queries through an external configuration file, enabling the tool to adapt to different search criteria without code modifications.

## Usage
To use DataJobsScraper, configure your search parameters in the `scrapper_config.json` file, including the base URL for job listings, search criteria like levels and categories, and other settings like headers and timeouts.

## Contribution
Contributions to DataJobsScraper are welcome! Whether you have suggestions for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.
