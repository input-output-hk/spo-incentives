import pandas as pd
import glob
import os
import re

def combine_epoch_csvs(output_filename="all_epochs_summary.csv"):
    """
    Finds all 'epoch_*_summary.csv' files in the current directory,
    adds an 'epoch' column to each, combines them, and saves to a new CSV.
    """
    # Use glob to find all files that match the pattern
    # This makes the script flexible for any number of epoch files.
    file_pattern = "epoch_*_summary.csv"
    csv_files = glob.glob(file_pattern)
    
    if not csv_files:
        print(f"No files found matching the pattern '{file_pattern}'.")
        print("Please make sure the script is in the same folder as your CSV files.")
        return

    print(f"Found {len(csv_files)} files to combine.")
    
    # List to hold each DataFrame
    all_dataframes = []
    
    # Loop through the list of files
    for f in csv_files:
        try:
            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(f)
            
            # --- Add the Epoch Column ---
            # Use a regular expression to find the number in the filename
            match = re.search(r'epoch_(\d+)_summary.csv', os.path.basename(f))
            if match:
                epoch_number = int(match.group(1))
                df['epoch'] = epoch_number
                all_dataframes.append(df)
                print(f"Processed '{f}' for epoch {epoch_number}.")
            else:
                print(f"Warning: Could not extract epoch number from '{f}'. Skipping file.")

        except Exception as e:
            print(f"Error processing file {f}: {e}")

    if not all_dataframes:
        print("No data was processed. Exiting.")
        return
        
    # Concatenate all the DataFrames into one
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # --- Reorder columns to have 'epoch' first ---
    cols = ['epoch'] + [col for col in combined_df.columns if col != 'epoch']
    combined_df = combined_df[cols]
    
    # **FIX:** Define a custom sort order for the 'stake_range' column
    stake_range_order = [
        'Inactive',
        '< 3M',
        '3M - 10M',
        '10M - 20M',
        '20M - 30M',
        '30M - 40M',
        '40M - 50M',
        '50M - 60M',
        '60M - 70M',
        '> 70M',
        '--- TOTALS ---'
    ]

    # Convert the 'stake_range' column to a categorical type with the specified order
    combined_df['stake_range'] = pd.Categorical(combined_df['stake_range'], categories=stake_range_order, ordered=True)
    
    # Sort the final DataFrame by epoch and then by the custom stake_range order
    combined_df = combined_df.sort_values(by=['epoch', 'stake_range']).reset_index(drop=True)
    
    # Save the combined DataFrame to a new CSV file
    combined_df.to_csv(output_filename, index=False)
    
    print(f"\nSuccess! All data has been combined into '{output_filename}'.")
    print(f"Total rows in new file: {len(combined_df)}")

if __name__ == '__main__':
    # You will need pandas library. If you don't have it, run:
    # pip install pandas
    combine_epoch_csvs()

