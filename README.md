# Continent & Country Demographics Data Visualisation

This project explores continent and country-level socio-economic and health demographics using interactive data visualisations. The visualisations are built with [Altair](https://altair-viz.github.io/) (Vega-Lite) in Python, and data preprocessing is performed using [pandas](https://pandas.pydata.org/).

## Features

- Interactive dashboards visualising key demographic, socio-economic, and health indicators.
- Data preprocessing and cleaning using pandas in Jupyter Notebook.
- Visualisations generated with Altair and exported as standalone HTML dashboards.
- Easy-to-use and shareable HTML dashboards—no server required.

## Repository Structure

- `visualisations.py` — Generates the interactive dashboards and exports them as HTML files.
- `preprocessing.ipynb` — Used for data preprocessing and exploration.
- `dashboard.html` and `dashboard-1.html` — Dashboard HTML files; open these in your browser to view the final visualisations.
- `README.md` — Project overview and instructions.

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "CSC3833 Data Visualisation Coursework"
```

### 2. Install Dependencies

Ensure you have Python 3.7+ installed. Install all required packages using the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Data Preprocessing

Open the Jupyter Notebook(s) in this repository to preprocess and clean the data:

```bash
jupyter notebook
```

Follow the notebook instructions to prepare the dataset.

### 4. Generate Dashboards

Run the `visualisations.py` script to generate the interactive dashboards:

```bash
python visualisations.py
```

This will create HTML files for each dashboard in the project directory.

### 5. View Dashboards

Open any of the generated `.html` dashboard files in your web browser to explore the visualisations.

## Notes

- All visualisations are self-contained in HTML files and require no additional setup to view.
- For any issues or questions, please refer to the code comments or contact the project maintainer.

---

