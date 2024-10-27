import pandas as pd


# Function to display results to the console (or to a logger)
def display_result(result):
    if not result['In_Directory']:
        print(f"Processed: {result['Name']}, not in directory")
    elif result['Multiple_Results']:
        print(f"Processed: {result['Name']}, Multiple results found")
    else:
        print(
            f"Processed: {result['Name']}, Directory Name: {result['Directory_Name']}, Email: {result['Email']}, Phone: {result['Phone']}, Location: {result['Location']}, Websites: {result['Websites']}, Department: {result['Department']}, Supervisor/PI: {result['Supervisor/PI']}")


# Function to export results to CSV
def export_to_csv(results, filename):
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)
    print(f"Data exported to {filename}")
