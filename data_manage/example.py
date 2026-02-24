"""Example usage of DataManager."""

import logging

from data_manager import DataManager

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize
dm = DataManager("./my_project_data")

# Load multiple formats
sales = dm.load("sales.csv")
customers = dm.load("customers.xlsx", sheet_name="Q1")
events = dm.load("events.json")

print(f"Sales: {len(sales)} rows")
print(f"Customers: {len(customers)} rows")
print(f"Events: {len(events)} rows")

# Inspect metadata
print(f"Sales source: {sales.attrs['source_file']}")
print(f"Sales checksum: {sales.attrs['checksum']}")

# Merge and process
merged = sales.merge(customers, on="customer_id", how="left")
merged["total"] = merged["quantity"] * merged["price"]

# Save in different formats
dm.save(merged, "processed/merged.parquet")  # Best for storage
dm.save(merged, "processed/merged.csv")  # For sharing
dm.save(merged, "processed/merged.xlsx")  # For Excel users

# Quick file info (without loading)
info = dm.get_info("processed/merged.parquet")
print(f"Parquet size: {info['size_mb']:.2f} MB")
print(f"Rows: {info.get('row_count', 'N/A')}")

# List all CSV files
csv_files = dm.list_files("**/*.csv")
print(f"Found {len(csv_files)} CSV files")
