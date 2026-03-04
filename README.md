# Business Intelligence Dashboard


## the link to the perview : https://bi-tp01.streamlit.app/


## Quick Overview
- Streamlit application addressing the “CS - 2ème Année” objectives: data modeling, storage, and dynamic analysis of sales, purchases, and margins.
- Example datasets included (Tableau.01 & Tableau.02) with the option to upload custom CSV/Excel files.
- Three tabs deliver the requested analyses:
  1. **Sales** – Montant TTC and Quantity indicators, filters from Product through Year.
  2. **Purchases** – Cost (TTC) and Quantity indicators, filters by Product/Supplier through Year.
  3. **Margins** – Combined sales/purchases view computing gross margin and margin rate.

## Analysis Questions Covered
### Sales table
- Products sold after **1 February 2025**.
- Product ranking by **revenue**, **sales type**, and **year** (bar charts).
- Top clients by **wilaya** and **legal form** (bar charts + treemap).
- Quantities by **category**, **sales type**, **month**, and **year** (stacked bars + lines + sunburst).
- Identification of the **most profitable category**.

### Purchase table
- Products purchased in **2024**.
- Quantities by **purchase type**, **month**, and **year** (bars + stacked areas).
- Supplier dominance by **product category** (bars + sunburst).
- Category with the **highest total cost** (card + donut chart).

### Margins (merged model)
- Gross margin and margin rate by **product**, **category**, **wilaya**, **month**, **year**.
- Time comparison of **CA vs Cost vs Margin**.
- Treemap showing category/product contributions to positive margins.

## Requirements
- Python 3.9+
- Dependencies listed in `requirements.txt` (`pip install -r requirements.txt`).
- Two data files:
  - `sales table .csv` (Tableau.01 structure)
  - `purchases table .csv` (Tableau.02 structure)

## Run
```bash
pip install -r requirements.txt
streamlit run BI.py
```
The app opens in your browser (default http://localhost:8501).

## How to Use
1. From the sidebar, upload **both tables** (sales and purchases). Built-in data is only for demo.
2. Open the Sales, Purchases, or Margins tab and apply any filters (Product, Category, Month, Year, etc.).
3. KPI cards, charts, and tables refresh instantly and answer all analysis questions above.

### Client presentation tips
- The intro card at the top recalls the pedagogical objectives and the three-part structure.
- Each analysis question is labeled with a dedicated section title.
- “Filtered data” expanders let you show the raw tables when required.

## Sample data
The provided `sales table .csv` and `purchases table .csv` mirror the values from the assignment tables so you can validate each visualization quickly.

---
Need extra indicators or visuals? Open `BI.py`, follow the existing section pattern, and reuse the helper functions (filters, themes, treemaps, etc.).