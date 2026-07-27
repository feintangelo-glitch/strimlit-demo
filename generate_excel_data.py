import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_excel_test_dataset(output_path="sample_excel_test_data.xlsx", csv_path="sample_google_sheets_data.csv", num_sales=1200, seed=42):
    """
    Generates a multi-tab Excel file and a Google Sheets compatible CSV test dataset.
    """
    np.random.seed(seed)
    
    # ----------------------------------------------------
    # TAB 1: Sales & Operations
    # ----------------------------------------------------
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 7, 25)
    date_range_days = (end_date - start_date).days
    
    categories = {
        "Agricultural Machinery": [
            ("Four-Wheel Tractors", 800000, 1500000),
            ("Rice Transplanters", 150000, 350000),
            ("Combine Harvesters", 1200000, 2200000),
            ("Solar Irrigation Systems", 250000, 600000),
            ("Power Tillers", 60000, 140000)
        ],
        "Fertilizers & Soil Health": [
            ("Organic Fertilizer (50kg)", 400, 850),
            ("Inorganic NPK Blend", 1100, 2200),
            ("Bio-Inoculant Strains", 300, 750),
            ("Soil Conditioner Granules", 500, 1200)
        ],
        "High-Value Crops & Seeds": [
            ("Certified Hybrid Rice Seeds", 1500, 3200),
            ("High-Yield Corn Seeds", 1800, 3800),
            ("Vegetable Seed Packs", 250, 800),
            ("Fruit Tree Saplings Batch", 800, 2500)
        ],
        "Post-Harvest Facilities": [
            ("Multi-Crop Dryer Unit", 450000, 950000),
            ("Cold Storage Module", 1200000, 3000000),
            ("Hermetic Storage Cocoons", 15000, 45000),
            ("Rice Mill Processing Line", 850000, 1800000)
        ]
    }
    
    provinces = ["Abra", "Apayao", "Benguet", "Ifugao", "Kalinga", "Mountain Province"]
    regions = ["CAR", "Region I", "Region II", "Region III"]
    sales_channels = ["Direct DA Grant", "LGU Co-op Procurement", "Commercial Agri-Dealer", "Farmer Association"]
    statuses = ["Completed", "Delivered", "In Transit", "Under Review", "Pending Approval"]
    status_weights = [0.60, 0.20, 0.10, 0.06, 0.04]
    
    sales_records = []
    cat_names = list(categories.keys())
    
    for i in range(num_sales):
        order_id = f"EXP-{30000 + i}"
        days_offset = int(np.random.randint(0, date_range_days))
        txn_date = start_date + timedelta(days=days_offset)
        
        cat = np.random.choice(cat_names, p=[0.30, 0.30, 0.25, 0.15])
        prod_tuple = categories[cat][np.random.randint(0, len(categories[cat]))]
        prod_name = prod_tuple[0]
        
        unit_price = round(float(np.random.uniform(prod_tuple[1], prod_tuple[2])), 2)
        qty = int(np.random.choice([1, 2, 3, 5, 10, 20, 50], p=[0.40, 0.25, 0.15, 0.10, 0.05, 0.03, 0.02]))
        
        gross_target = round(unit_price * qty, 2)
        discount_pct = float(np.random.choice([0.0, 0.05, 0.10, 0.15], p=[0.60, 0.25, 0.10, 0.05]))
        actual_revenue = round(gross_target * (1.0 - discount_pct), 2)
        
        cost_ratio = np.random.uniform(0.60, 0.82)
        cost = round(actual_revenue * cost_ratio, 2)
        profit = round(actual_revenue - cost, 2)
        
        prov = np.random.choice(provinces)
        reg = "CAR" if np.random.rand() > 0.15 else np.random.choice(regions)
        channel = np.random.choice(sales_channels)
        status = np.random.choice(statuses, p=status_weights)
        rating = int(np.random.choice([5, 4, 3, 2, 1], p=[0.55, 0.30, 0.10, 0.03, 0.02]))
        
        sales_records.append({
            "Transaction_ID": order_id,
            "Date": txn_date.strftime("%Y-%m-%d"),
            "Year": txn_date.year,
            "Month": txn_date.strftime("%b"),
            "Region": reg,
            "Province": prov,
            "Category": cat,
            "Item_Name": prod_name,
            "Channel": channel,
            "Quantity": qty,
            "Unit_Price_PHP": unit_price,
            "Target_Revenue_PHP": gross_target,
            "Actual_Revenue_PHP": actual_revenue,
            "Total_Cost_PHP": cost,
            "Net_Profit_PHP": profit,
            "Status": status,
            "Satisfaction_Score": rating
        })
        
    df_sales = pd.DataFrame(sales_records)
    
    # Save CSV copy for Google Sheets import
    df_sales.to_csv(csv_path, index=False)
    
    # ----------------------------------------------------
    # TAB 2: Regional Project Tracker
    # ----------------------------------------------------
    project_names = [
        "High-Value Crops Development Program (HVCDP)",
        "National Rice Program Machinery Distribution",
        "National Corn Program Seed Resiliency Project",
        "Organic Agriculture Infrastructure Enhancement",
        "Climate-Resilient Agriculture (CRA) Water Systems",
        "Post-Harvest Processing & Facility Upgrades",
        "Agri-Extension & Capability Building Workshops",
        "Soil Fertility Mapping & Diagnostic Lab Expansion"
    ]
    
    project_records = []
    proj_id_counter = 101
    for p_name in project_names:
        for prov in provinces:
            p_code = f"PRJ-{proj_id_counter}"
            proj_id_counter += 1
            
            p_target = int(np.random.randint(50, 600))
            accomplishment_pct = np.random.uniform(0.70, 1.15)
            p_actual = int(round(p_target * accomplishment_pct))
            
            b_target_k = round(float(np.random.uniform(500, 8000)), 2)
            ob_pct = np.random.uniform(0.75, 1.02)
            b_actual_k = round(b_target_k * ob_pct, 2)
            
            disb_pct = np.random.uniform(0.65, 0.98)
            disb_actual_k = round(b_actual_k * disb_pct, 2)
            
            status = "Completed" if accomplishment_pct >= 1.0 else ("On Track" if accomplishment_pct >= 0.85 else "Delayed")
            
            project_records.append({
                "Project_Code": p_code,
                "Program_Name": p_name,
                "Province": prov,
                "Physical_Target_Units": p_target,
                "Physical_Actual_Units": p_actual,
                "Accomplishment_Rate_Pct": round((p_actual / p_target) * 100, 1),
                "Obligation_Target_kPHP": b_target_k,
                "Obligation_Actual_kPHP": b_actual_k,
                "Disbursement_Actual_kPHP": disb_actual_k,
                "Financial_Execution_Rate_Pct": round((disb_actual_k / b_target_k) * 100, 1),
                "Status": status
            })
            
    df_projects = pd.DataFrame(project_records)
    
    # ----------------------------------------------------
    # TAB 3: Inventory & Logistics
    # ----------------------------------------------------
    inv_records = []
    item_id = 5001
    for cat, items in categories.items():
        for prod_name, min_p, max_p in items:
            for prov in provinces:
                stock = int(np.random.randint(10, 500))
                reorder = int(np.random.randint(30, 100))
                stock_status = "Optimal" if stock > reorder * 1.5 else ("Low Stock" if stock >= reorder else "Critical Reorder")
                unit_val = round(float((min_p + max_p) / 2), 2)
                
                inv_records.append({
                    "Stock_SKU": f"SKU-{item_id}",
                    "Category": cat,
                    "Item_Description": prod_name,
                    "Depot_Location": f"{prov} Central Hub",
                    "Stock_On_Hand": stock,
                    "Reorder_Level": reorder,
                    "Unit_Value_PHP": unit_val,
                    "Total_Inventory_Value_PHP": round(stock * unit_val, 2),
                    "Stock_Health": stock_status
                })
                item_id += 1
                
    df_inventory = pd.DataFrame(inv_records)
    
    # Write to multi-sheet Excel file
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_sales.to_excel(writer, sheet_name="Sales_&_Operations", index=False)
        df_projects.to_excel(writer, sheet_name="Project_Tracker", index=False)
        df_inventory.to_excel(writer, sheet_name="Inventory_Status", index=False)
        
    print(f"Successfully generated Excel dataset: {output_path} and CSV for Google Sheets: {csv_path}")
    return output_path, csv_path

if __name__ == "__main__":
    generate_excel_test_dataset()
