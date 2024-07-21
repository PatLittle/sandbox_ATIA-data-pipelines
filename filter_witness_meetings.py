import pandas as pd

def main():
    # Load the data
    ministers_csv_path = 'output.csv'
    meetings_csv_path = 'full_witness_meetings_output.csv'
    
    ministers_df = pd.read_csv(ministers_csv_path)
    meetings_df = pd.read_csv(meetings_csv_path)

    # Ensure witness_id is integer for matching
    ministers_df['witness_id'] = ministers_df['witness_id'].astype('Int64')

    # Filter the meetings_df to only include rows where witness_id matches those in ministers_df
    filtered_meetings_df = meetings_df[meetings_df['Witness ID'].isin(ministers_df['witness_id'])]

    # Add the disclosure_deadline column, which is 120 days after the Date field
    filtered_meetings_df['Date'] = pd.to_datetime(filtered_meetings_df['Date'])
    filtered_meetings_df['disclosure_deadline'] = filtered_meetings_df['Date'] + pd.DateOffset(days=120)

    # Save the filtered DataFrame to a new CSV file
    filtered_meetings_csv_path = 'minister_parl_comm_deadlines.csv'
    filtered_meetings_df.to_csv(filtered_meetings_csv_path, index=False)

    print(f'Filtered meetings CSV file saved to {filtered_meetings_csv_path}')

if __name__ == "__main__":
    main()
