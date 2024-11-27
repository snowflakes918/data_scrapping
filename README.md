# UC Directory Scraper

This project is a scalable and reusable Python tool to scrape staff and faculty directory information from various UC campus websites. It extracts details such as names, titles, emails, phone numbers, and departments, and outputs the data into CSV files.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Configuration](#configuration)
  - [Running the Scraper](#running-the-scraper)
- [Project Structure](#project-structure)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

---

## Prerequisites

- Python 3.8 or higher
- A Python virtual environment (recommended)
- Browser automation tools: [Playwright](https://playwright.dev/)

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/snowflakes918/data_scrapping.git
   cd uawDIC/
   pip install -r requirements.txt

2. **Set up a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

---

## Usage

### Configuration

1. **Modify `config.py`**:
   - Add campus-specific configurations, such as base URLs, input/output paths, and specific selectors.

   ```python
   CAMPUSES = {
       "ucsd": {
           "base_url": "https://itsweb.ucsd.edu/directory/search",
           "selectors": { ... },
       },
       "ucr": {
           "base_url": "https://profiles.ucr.edu/app/home/search",
           "selectors": { ... },
       },
   }
   ```

2. **Input File**:
   - Ensure your input CSV file is formatted with columns `first_name` and `last_name`.

3. **Output File**:
   - Define the output file path in the configuration for the corresponding campus.

---

### Running the Scraper

1. **Execute `main.py`**:
   Run the scraper for a specific campus:
   ```bash
   python dataScrap_main.py
   ```

---

## Project Structure for data scrappers

```
playwright_impl/
├── CommonUtils/
│   ├── scrape_utils.py      # Scraping logic
├── data/
│   ├── input/               # Input CSV files
│   ├── output/              # Output CSV files
├── configs/                 # Campus specific config
├── dataScrap_main.py        # Entry point for the scraper
├── scrapper_logic.py        # main logic for the scraper

```

---

## Examples

### Example Input (`data/input/ucsd_input.csv`)

| first_name | last_name  |
|------------|------------|
| John       | Doe        |
| Jane       | Smith      |

### Example Output (`data/output/ucsd_output.csv`)

| Name         | Title                 | Phone        | Email                  | Department          |
|--------------|-----------------------|--------------|------------------------|---------------------|
| John Doe     | Research Scientist    | (858) 123-4567 | john.doe@ucsd.edu      | Computer Science    |
| Jane Smith   | Professor             | (858) 987-6543 | jane.smith@ucsd.edu    | Biology Department  |

---

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
