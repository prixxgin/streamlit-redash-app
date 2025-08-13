import pandas as pd

def process_asn_pickup(input_file, output_file):
    # Read CSV and strip spaces from column names
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    df.columns = df.columns.str.strip()

    # Check required columns exist
    required_cols = {'pickup_hub_name', 'Week'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_cols}")

    # Create helper flag
    df['has_asn'] = df['pickup_hub_name'].str.contains('ASN', case=False, na=False)

    # Identify weeks containing ASN
    weeks_with_asn = df.loc[df['has_asn'], 'Week'].unique()

    # Create Column T
    df['T'] = df['Week'].apply(lambda w: 'ASN PICKUP' if w in weeks_with_asn else '')

    # Remove helper column
    df.drop(columns=['has_asn'], inplace=True)

    # Save result
    df.to_csv(output_file, index=False)
    print(f"✅ Processed file saved to: {output_file}")

# Example usage:
# process_asn_pickup("ASN Shipper Transition.csv", "output_with_asn.csv")
