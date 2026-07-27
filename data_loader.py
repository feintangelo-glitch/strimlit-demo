import pandas as pd
import numpy as np

EXCEL_FILE = "DARFOCAR-Physical and Financial Accomplishment Report.xlsx"

def clean_val(val):
    if pd.isna(val):
        return 0
    try:
        res = float(val)
        return 0 if np.isnan(res) else res
    except:
        return 0

def load_pmed_fod_data(excel_path=EXCEL_FILE):
    """
    Parses PMED and FOD sheets from DA-RFO CAR accomplishment report.
    Returns structured DataFrame for Physical & Financial targets/accomplishments.
    """
    excel = pd.ExcelFile(excel_path)
    records = []
    
    for sheet_name in ["PMED", "FOD"]:
        if sheet_name not in excel.sheet_names:
            continue
            
        df = pd.read_excel(excel, sheet_name=sheet_name, header=None)
        
        current_sub = "General Operations"
        for r in range(6, len(df)):
            row = df.iloc[r]
            val0 = str(row[0]).strip() if pd.notna(row[0]) else ""
            
            if not val0 or "Source:" in val0 or "GRAND TOTAL" in val0:
                continue
                
            if val0 in ["PLANNING, MONITORING AND EVALUATION DIVISION", "FIELD OPERATIONS DIVISION", "ICTMS", "DoPP-PMED"]:
                current_sub = val0
                continue
                
            if val0 in ["Sub-total", "TOTAL", "0"]:
                continue
                
            ppa_name = val0
            indicator = str(row[1]).strip() if pd.notna(row[1]) else ""
            unit = str(row[2]).strip() if pd.notna(row[2]) else ""
            
            p_q1_target = clean_val(row[7])
            p_q1_actual = clean_val(row[22])
            
            p_q2_target = clean_val(row[37])
            p_q2_actual = clean_val(row[52])
            
            p_q3_target = clean_val(row[67])
            p_q3_actual = clean_val(row[82])
            
            p_q4_target = clean_val(row[97])
            p_q4_actual = clean_val(row[112])
            
            p_annual_target = clean_val(row[148]) or (p_q1_target + p_q2_target + p_q3_target + p_q4_target)
            p_annual_actual = clean_val(row[149]) or (p_q1_actual + p_q2_actual + p_q3_actual + p_q4_actual)
            
            f_ob_q1_target = clean_val(row[12])
            f_ob_q1_actual = clean_val(row[27])
            f_ob_annual_target = clean_val(row[152]) or f_ob_q1_target
            f_ob_annual_actual = clean_val(row[153]) or f_ob_q1_actual
            
            f_disb_q1_target = clean_val(row[13])
            f_disb_q1_actual = clean_val(row[32])
            f_disb_annual_target = clean_val(row[156]) or f_disb_q1_target
            f_disb_annual_actual = clean_val(row[157]) or f_disb_q1_actual
            
            records.append({
                "Division": sheet_name,
                "Section": current_sub,
                "PPA_Name": ppa_name,
                "Indicator": indicator,
                "Unit": unit,
                "Physical_Target_Q1": p_q1_target,
                "Physical_Actual_Q1": p_q1_actual,
                "Physical_Target_Q2": p_q2_target,
                "Physical_Actual_Q2": p_q2_actual,
                "Physical_Target_Q3": p_q3_target,
                "Physical_Actual_Q3": p_q3_actual,
                "Physical_Target_Q4": p_q4_target,
                "Physical_Actual_Q4": p_q4_actual,
                "Physical_Annual_Target": p_annual_target,
                "Physical_Annual_Actual": p_annual_actual,
                "Obligation_Target_kPHP": f_ob_annual_target,
                "Obligation_Actual_kPHP": f_ob_annual_actual,
                "Disbursement_Target_kPHP": f_disb_annual_target,
                "Disbursement_Actual_kPHP": f_disb_annual_actual,
            })
            
    df_result = pd.DataFrame(records)
    if not df_result.empty:
        df_result["Physical_Rate_Pct"] = np.where(
            df_result["Physical_Annual_Target"] > 0,
            np.round(df_result["Physical_Annual_Actual"] / df_result["Physical_Annual_Target"] * 100, 1),
            0.0
        )
        df_result["Obligation_Rate_Pct"] = np.where(
            df_result["Obligation_Target_kPHP"] > 0,
            np.round(df_result["Obligation_Actual_kPHP"] / df_result["Obligation_Target_kPHP"] * 100, 1),
            0.0
        )
        df_result["Disbursement_Rate_Pct"] = np.where(
            df_result["Disbursement_Target_kPHP"] > 0,
            np.round(df_result["Disbursement_Actual_kPHP"] / df_result["Disbursement_Target_kPHP"] * 100, 1),
            0.0
        )
    return df_result


def load_rsbsa_data(excel_path=EXCEL_FILE):
    """
    Parses VERIFIED_adjusted, NEW_adjusted, and UPDATED_adjusted sheets from DA-RFO CAR report.
    Returns structured DataFrame for RSBSA farmer/fisher registration stats.
    """
    excel = pd.ExcelFile(excel_path)
    records = []
    
    sheet_mapping = {
        "VERIFIED_adjusted": "Verified Records",
        "NEW_adjusted": "New Registrations",
        "UPDATED_adjusted": "Updated Records"
    }
    
    for sheet_key, status_label in sheet_mapping.items():
        if sheet_key not in excel.sheet_names:
            continue
            
        df = pd.read_excel(excel, sheet_name=sheet_key, header=None)
        current_region = "CORDILLERA ADMINISTRATIVE REGION (CAR)"
        
        for r in range(10, len(df)):
            row = df.iloc[r]
            name = str(row[0]).strip() if pd.notna(row[0]) else ""
            
            if not name or "GRAND TOTAL" in name or name == "reported":
                continue
                
            clean_name = name.replace("        ", "").replace("   ", "").strip()
            
            is_province = (
                clean_name in ["Abra", "Apayao", "Benguet (w/ HUC)", "Ifugao", "Kalinga", "Mountain Province"] or
                name.startswith("        ") or name.startswith("   ")
            )
            
            if name.startswith("REGION") or "CORDILLERA" in name:
                current_region = clean_name
                is_province = False
            
            val_2024 = clean_val(row[17]) or clean_val(row[1])
            val_2025 = clean_val(row[48])
            val_grand = clean_val(row[49]) or (val_2024 + val_2025)
            
            jan = clean_val(row[19]) or clean_val(row[1])
            feb = clean_val(row[22]) or clean_val(row[2])
            mar = clean_val(row[25]) or clean_val(row[3])
            apr = clean_val(row[29]) or clean_val(row[5])
            may = clean_val(row[32]) or clean_val(row[6])
            jun = clean_val(row[35]) or clean_val(row[7])
            jul = clean_val(row[38]) or clean_val(row[9])
            aug = clean_val(row[41]) or clean_val(row[10])
            sep = clean_val(row[42]) or clean_val(row[11])
            oct_val = clean_val(row[44]) or clean_val(row[13])
            nov = clean_val(row[45]) or clean_val(row[14])
            dec = clean_val(row[46]) or clean_val(row[15])
            
            records.append({
                "Status": status_label,
                "Region": current_region,
                "Name": clean_name,
                "Is_Province": is_province,
                "Total_2024": int(val_2024),
                "Total_2025": int(val_2025),
                "Grand_Total": int(val_grand),
                "Jan": int(jan),
                "Feb": int(feb),
                "Mar": int(mar),
                "Apr": int(apr),
                "May": int(may),
                "Jun": int(jun),
                "Jul": int(jul),
                "Aug": int(aug),
                "Sep": int(sep),
                "Oct": int(oct_val),
                "Nov": int(nov),
                "Dec": int(dec)
            })
            
    return pd.DataFrame(records)

if __name__ == "__main__":
    df_pmed = load_pmed_fod_data()
    print(f"PMED/FOD Loaded: {len(df_pmed)} rows")
    df_rsbsa = load_rsbsa_data()
    print(f"RSBSA Loaded: {len(df_rsbsa)} rows")
