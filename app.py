import pandas as pd

# === Read CSV ===
df = pd.read_csv("ASN Shipper Transition V2 - Raw Shippers (From Metabase).csv")

# Create a helper flag for rows containing "ASN" in pickup_hub_name
df['has_asn'] = df['pickup_hub_name'].str.contains('ASN', case=False, na=False)

# Find weeks that have ASN in any pickup_hub_name
weeks_with_asn = df.loc[df['has_asn'], 'Week'].unique()

# Create new column 'ASN PICKUP'
df['ASN PICKUP'] = df['Week'].apply(lambda w: 'YES' if w in weeks_with_asn else 'NO')

# Drop helper column
df.drop(columns=['has_asn'], inplace=True)

# Save result
df.to_csv("output_with_asn_pickup.csv", index=False)

print("✅ File saved as output_with_asn_pickup.csv")
