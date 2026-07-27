import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_sample_data(num_records=3500, file_path="sales_data.csv", seed=42):
    """
    Generates a realistic synthetic sales dataset and saves it to a CSV file.
    """
    np.random.seed(seed)
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 7, 25)
    date_range_days = (end_date - start_date).days
    
    # Categories & Products mapping with typical price ranges
    catalog = {
        "Electronics": [
            ("Laptops & Workstations", 1200, 2500),
            ("Smartphones & Tablets", 600, 1400),
            ("Monitors & Displays", 250, 800),
            ("Wireless Audio", 100, 350),
            ("Smart Wearables", 150, 450)
        ],
        "Software & Cloud": [
            ("Enterprise CRM License", 500, 3000),
            ("Cloud Analytics Suite", 800, 4500),
            ("Cybersecurity Suite", 400, 2200),
            ("DevOps Productivity Tools", 300, 1500),
            ("AI Assistant Subscription", 200, 1000)
        ],
        "Office Furniture": [
            ("Ergonomic Executive Chairs", 350, 950),
            ("Adjustable Standing Desks", 500, 1400),
            ("Acoustic Office Pods", 1500, 5000),
            ("Conference Tables", 800, 2800),
            ("LED Desk Lighting", 60, 180)
        ],
        "Office Supplies": [
            ("High-Volume Printers", 400, 1200),
            ("Paper & Stationeries Pack", 30, 120),
            ("Storage & Archiving Units", 80, 300),
            ("Breakroom Supplies", 40, 200),
            ("Presentation Equipment", 150, 600)
        ]
    }
    
    regions_countries = {
        "North America": ["USA", "Canada", "Mexico"],
        "Europe": ["United Kingdom", "Germany", "France", "Netherlands", "Spain"],
        "Asia Pacific": ["Japan", "Australia", "Singapore", "India", "South Korea"],
        "Latin America": ["Brazil", "Chile", "Colombia"],
        "Middle East & Africa": ["UAE", "Saudi Arabia", "South Africa"]
    }
    
    customer_segments = ["Enterprise", "Corporate", "Small Business", "Consumer"]
    segment_weights = [0.25, 0.40, 0.25, 0.10]
    
    shipping_statuses = ["Delivered", "Shipped", "Processing", "Cancelled"]
    status_weights = [0.82, 0.10, 0.05, 0.03]
    
    records = []
    customer_pool = [f"CUST-{1000 + i}" for i in range(400)]
    
    categories = list(catalog.keys())
    cat_weights = [0.35, 0.30, 0.20, 0.15]
    
    for i in range(num_records):
        order_id = f"ORD-{20000 + i}"
        
        # Random date with slight seasonal trend
        random_days = np.random.randint(0, date_range_days)
        order_date = start_date + timedelta(days=int(random_days))
        
        category = np.random.choice(categories, p=cat_weights)
        product_info = catalog[category][np.random.randint(0, len(catalog[category]))]
        product_name = product_info[0]
        unit_price = round(float(np.random.uniform(product_info[1], product_info[2])), 2)
        
        # Quantity
        quantity = int(np.random.choice([1, 2, 3, 4, 5, 8, 10, 15], p=[0.35, 0.25, 0.15, 0.10, 0.08, 0.04, 0.02, 0.01]))
        
        # Discount
        discount_pct = float(np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20], p=[0.50, 0.25, 0.15, 0.07, 0.03]))
        
        sales_revenue = round(unit_price * quantity * (1.0 - discount_pct), 2)
        
        # Cost & Profit margin varies by category
        if category == "Software & Cloud":
            margin = np.random.uniform(0.70, 0.88)
        elif category == "Electronics":
            margin = np.random.uniform(0.20, 0.40)
        elif category == "Office Furniture":
            margin = np.random.uniform(0.35, 0.55)
        else:
            margin = np.random.uniform(0.30, 0.50)
            
        profit = round(sales_revenue * margin, 2)
        cost = round(sales_revenue - profit, 2)
        
        region = np.random.choice(list(regions_countries.keys()), p=[0.40, 0.30, 0.18, 0.07, 0.05])
        country = np.random.choice(regions_countries[region])
        
        segment = np.random.choice(customer_segments, p=segment_weights)
        customer_id = np.random.choice(customer_pool)
        shipping_status = np.random.choice(shipping_statuses, p=status_weights)
        
        # Satisfaction rating (1 to 5)
        if shipping_status == "Cancelled":
            rating = np.random.choice([1, 2], p=[0.7, 0.3])
        else:
            rating = np.random.choice([3, 4, 5, 2, 1], p=[0.25, 0.45, 0.22, 0.05, 0.03])
            
        records.append({
            "Order_ID": order_id,
            "Order_Date": order_date.strftime("%Y-%m-%d"),
            "Customer_ID": customer_id,
            "Customer_Segment": segment,
            "Region": region,
            "Country": country,
            "Product_Category": category,
            "Product_Name": product_name,
            "Unit_Price": unit_price,
            "Quantity": quantity,
            "Discount_Pct": discount_pct,
            "Sales_Revenue": sales_revenue,
            "Cost": cost,
            "Profit": profit,
            "Shipping_Status": shipping_status,
            "Satisfaction_Rating": rating
        })
        
    df = pd.DataFrame(records)
    df.to_csv(file_path, index=False)
    return df

if __name__ == "__main__":
    df = generate_sample_data()
    print(f"Sample data generated successfully with {len(df)} records.")
