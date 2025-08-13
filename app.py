import pandas as pd

# === CONFIG ===
INPUT_FILE = "pickups.csv"   # CSV in your repo
OUTPUT_FILE = "pickups_with_asn.csv"  # Output file with new column

# 1️⃣ Read the CSV
df = pd.read_csv(INPUT_FILE)

# 2️⃣ Check for 'ASN' keyword in pickup_hub_name (case-insensitive)
df["has_asn"] = df["pickup_hub_name"].str.contains("ASN", case=False, na=False)

# 3️⃣ Find all weeks that have ASN pickups
weeks_with_asn = df.loc[df["has_asn"], "week"].unique()

# 4️⃣ Mark ASN PICKUP per row
df["ASN PICKUP"] = df["week"].apply(lambda w: "Yes" if w in weeks_with_asn else "No")

# 5️⃣ Drop helper column (optional)
df.drop(columns=["has_asn"], inplace=True)

# 6️⃣ Save output
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Updated file saved as {OUTPUT_FILE}")
