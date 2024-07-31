import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chi2

# Load the spreadsheet
file_path = 'study_data_ex.xlsx'
spreadsheet = pd.ExcelFile(file_path)

# Load the sheet
df = pd.read_excel(spreadsheet, sheet_name=0)

# Converting non-string entries to string to extract numeric values
df['Preop- BMI (kg/m2)'] = df['Preop- BMI (kg/m2)'].astype(str).str.extract(r'(\d+\.\d+)').astype(float)
df['Operation time (min)'] = df['Operation time (min)'].astype(str).str.extract(r'(\d+\.\d+)').astype(float)
df['Length of stay (days)'] = pd.to_numeric(df['Length of stay (days)'], errors='coerce')
df['# of Patients'] = pd.to_numeric(df['# of Patients'], errors='coerce')

# Ensure 'Postop complications' and 'Reoperation' columns contain numeric values
df['Postop complications'] = pd.to_numeric(df['Postop complications'], errors='coerce')
df['Reoperation'] = pd.to_numeric(df['Reoperation'], errors='coerce')

# Filter out rows with NaN in '# of Patients'
df = df.dropna(subset=['# of Patients'])

# Calculate total number of patients, total postop complications, total reoperations
total_patients = df['# of Patients'].sum()
total_postop_complications = df['Postop complications'].sum()
total_reoperations = df['Reoperation'].sum()

# Filter out rows with NaN in necessary columns for weighted calculations
preop_bmi_data = df.dropna(subset=['Preop- BMI (kg/m2)'])
operation_time_data = df.dropna(subset=['Operation time (min)'])
length_of_stay_data = df.dropna(subset=['Length of stay (days)'])

# Function to calculate weighted mean and standard deviation
def weighted_avg_and_std(values, weights):
    average = np.average(values, weights=weights)
    variance = np.average((values - average) ** 2, weights=weights)
    return average, np.sqrt(variance)

# Calculate weighted averages and standard deviations
average_preop_bmi, sd_preop_bmi = weighted_avg_and_std(
    preop_bmi_data['Preop- BMI (kg/m2)'], preop_bmi_data['# of Patients']
)
average_operation_time, sd_operation_time = weighted_avg_and_std(
    operation_time_data['Operation time (min)'], operation_time_data['# of Patients']
)

# Calculate average length of stay (without standard deviation) weighted
average_length_of_stay = np.average(
    length_of_stay_data['Length of stay (days)'], weights=length_of_stay_data['# of Patients']
)

# Calculate Odds Ratios (OR) and 95% Confidence Intervals (CI) for categorical outcomes
def calculate_or_ci(event, total):
    or_value = (event / (total - event))
    se = np.sqrt(1/event + 1/(total - event))
    ci_lower = np.exp(np.log(or_value) - 1.96 * se)
    ci_upper = np.exp(np.log(or_value) + 1.96 * se)
    return or_value, ci_lower, ci_upper

or_postop_complications, ci_lower_postop, ci_upper_postop = calculate_or_ci(total_postop_complications, total_patients)
or_reoperations, ci_lower_reop, ci_upper_reop = calculate_or_ci(total_reoperations, total_patients)

# Assess heterogeneity between studies using Cochran’s Q statistic
def cochran_q_statistic(events, total):
    observed = events / total
    expected = np.sum(events) / np.sum(total)
    q = np.sum((events - expected * total) ** 2 / (expected * (1 - expected) * total))
    return q

q_postop_complications = cochran_q_statistic(df['Postop complications'].fillna(0), df['# of Patients'])
q_reoperations = cochran_q_statistic(df['Reoperation'].fillna(0), df['# of Patients'])

# Degrees of freedom
df_postop_complications = len(df) - 1
df_reoperations = len(df) - 1

# Calculate p-value for Cochran’s Q statistic
p_value_postop_complications = 1 - chi2.cdf(q_postop_complications, df_postop_complications)
p_value_reoperations = 1 - chi2.cdf(q_reoperations, df_reoperations)

# Results
results = {
    "Total number of patients": total_patients,
    "Total postoperative complications": total_postop_complications,
    "Total reoperations": total_reoperations,
    "Average pre-op BMI": f"{average_preop_bmi:.2f} (SD: {sd_preop_bmi:.2f})",
    "Average operation time": f"{average_operation_time:.2f} minutes (SD: {sd_operation_time:.2f})",
    "Average length of stay": f"{average_length_of_stay:.2f} days",
    "OR Postop Complications": f"{or_postop_complications:.2f} (CI: {ci_lower_postop:.2f}-{ci_upper_postop:.2f})",
    "OR Reoperations": f"{or_reoperations:.2f} (CI: {ci_lower_reop:.2f}-{ci_upper_reop:.2f})",
    "Cochran’s Q Postop Complications": f"{q_postop_complications:.2f} (p-value: {p_value_postop_complications:.2f})",
    "Cochran’s Q Reoperations": f"{q_reoperations:.2f} (p-value: {p_value_reoperations:.2f})"
}

# Prepare data for table
data = [
    ["Total number of patients", total_patients],
    ["Total postoperative complications", total_postop_complications],
    ["Total reoperations", total_reoperations],
    ["Average pre-op BMI", f"{average_preop_bmi:.2f} (SD: {sd_preop_bmi:.2f})"],
    ["Average operation time", f"{average_operation_time:.2f} minutes (SD: {sd_operation_time:.2f})"],
    ["Average length of stay", f"{average_length_of_stay:.2f} days"],
    ["OR Postop Complications", f"{or_postop_complications:.2f} (CI: {ci_lower_postop:.2f}-{ci_upper_postop:.2f})"],
    ["OR Reoperations", f"{or_reoperations:.2f} (CI: {ci_lower_reop:.2f}-{ci_upper_reop:.2f})"],
    ["Cochran’s Q Postop Complications", f"{q_postop_complications:.2f} (p-value: {p_value_postop_complications:.2f})"],
    ["Cochran’s Q Reoperations", f"{q_reoperations:.2f} (p-value: {p_value_reoperations:.2f})"]
]

# Create a table
fig, ax = plt.subplots()
ax.axis('off')
table = ax.table(cellText=data, colLabels=["Metric", "Value"], cellLoc='center', loc='center')

# Adjust table properties
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)

# Show plot
plt.show()