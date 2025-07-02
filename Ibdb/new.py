import os
import pandas as pd

# Set the folder path containing your CSV files
folder_path = 'theatres_details'  # Change this to your folder path

# List all CSV files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Create an empty list to hold DataFrames
dataframes = []

# Loop through and read each CSV file, then append to the list
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    dataframes.append(df)

# Concatenate all DataFrames in the list into one
combined_df = pd.concat(dataframes, ignore_index=True)

# Optionally save the result to a new CSV file
combined_df.to_csv('combined_data.csv', index=False)

print("All CSV files have been successfully combined.")



"""

def add_theatre_column_to_folder(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".csv") and "_details" in file:
            file_path = os.path.join(folder_path, file)

            # Remove '_details.csv' from the filename to get the theatre name
            theatre_name = file.replace("_details.csv", "").strip()

            try:
                df = pd.read_csv(file_path)
                df["theatre"] = theatre_name.title()  # Title-case formatting

                # Save changes (overwrite original)
                df.to_csv(file_path, index=False)
                print(f"✅ 'theatre' column added to '{file}' with value: '{theatre_name.title()}'")
            
            except Exception as e:
                print(f"❌ Error processing {file}: {e}")

# Example usage
add_theatre_column_to_folder("theatres_details")
"""