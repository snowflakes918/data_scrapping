import json

from scraper_logic import scrape_directory

if __name__ == "__main__":
    # base_dir = os.path.dirname(os.path.abspath(__file__))

    # Load UCSD configuration
    with open("configs/ucsd_config.json") as f:
        ucsd_config = json.load(f)

    # Load UC Berkeley configuration
    with open("configs/ucb_config.json") as f:
        ucb_config = json.load(f)

    # Load UC Irvine configuration
    with open("configs/uci_config.json") as f:
        uci_config = json.load(f)

    # Load UC Riverside configuration
    with open("configs/ucr_config.json") as f:
        ucr_config = json.load(f)

    # Scrape UCSD directory
    ucsd_results = scrape_directory(ucsd_config)
    ucsd_results.to_csv(ucsd_config["output_file"], index=False)
    print(f"Scraping complete for UCSD! Data saved to {ucsd_config['output_file']}.")

    # Scrape UC Berkeley directory
    ucb_results = scrape_directory(ucb_config)
    ucb_results.to_csv(ucb_config["output_file"], index=False)
    print(f"Scraping complete for UC Berkeley! Data saved to {ucb_config['output_file']}.")

    # Scrape UC Irvine directory
    uci_results = scrape_directory(uci_config)
    uci_results.to_csv(uci_config["output_file"], index=False)
    print(f"Scraping complete for UC Berkeley! Data saved to {uci_config['output_file']}")

    # Scrape UC Riverside directory
    ucr_results = scrape_directory(ucr_config)
    ucr_results.to_csv(ucr_config["output_file"], index=False)
    print(f"Scraping complete for UC Berkeley! Data saved to {ucr_config['output_file']}")
