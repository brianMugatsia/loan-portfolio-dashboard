# Loan Portfolio Dashboard (Python + Streamlit)

## 1. Requirements
- Python 3.10 or newer
- Your loan portfolio Excel workbook (`.xlsx`) or CSV file

## 2. Open the project folder
Extract the ZIP file, then open the extracted `loan_portfolio_dashboard` folder in VS Code.

## 3. Create and activate a virtual environment (Windows PowerShell)
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

If you use Git Bash:
```bash
python -m venv venv
source venv/Scripts/activate
```

## 4. Install packages
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Run the dashboard
```bash
streamlit run app.py
```

Streamlit will open the dashboard in your browser. If it does not, open:
`http://localhost:8501`

## 6. Upload your Excel file
Use the file uploader in the left sidebar.

The app expects these exact column headers:
- Branch
- Loan Type
- Disbursement Date
- Principal Amount
- Outstanding Balance
- Status

Optional columns:
- Interest Rate (%)
- Credit Score
- Risk Rating

The workbook can have a sheet named `Loan Portfolio`; the app reads the first sheet in the uploaded workbook by default. If your data is on another sheet, save/export that sheet separately or change `pd.read_excel` in `app.py` to specify its sheet name.

## Notes
- The dashboard does not modify your original Excel file.
- Missing optional columns are handled; their KPI/chart is shown as unavailable.
- PAR is calculated as overdue/defaulted outstanding balance divided by total outstanding balance. Confirm this matches your institution's definition.
