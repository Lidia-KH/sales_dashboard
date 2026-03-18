
# Sales Analytics & Forecasting Dashboard

An interactive data analytics dashboard built that transforms raw sales data into actionable business insights.
The application automatically analyzes revenue trends, product performance, marketing efficiency, inventory health, and future revenue forecasts.

This project demonstrates end-to-end data analytics workflow: data ingestion, cleaning, feature engineering, KPI computation, and forecasting visualization.

---

## Overview

Businesses often collect large volumes of transactional data but struggle to convert it into insights that support decision making.
This dashboard solves that problem by allowing users to upload a sales dataset and automatically generate analytics reports.

The system supports dynamic column mapping, meaning it can adapt to different dataset structures without manual preprocessing.

Key capabilities include:

* Automated revenue and profit analysis
* Customer acquisition cost (CAC) calculation
* Best-selling product identification
* Marketing performance insights
* Inventory health monitoring
* Time-series revenue forecasting

---

## Dashboard Features

### Sales Overview

Provides high-level KPIs and trend analysis:

* Total revenue
* Profit estimation
* Best-selling products
* Traffic source distribution
* Revenue growth over time

### Inventory Analytics

Monitors product stock levels and predicts potential stockouts.

Metrics include:

* Average daily product sales
* Inventory levels
* Estimated days until stock depletion
* Stock health classification

### Revenue Forecasting

Applies a regression-based time series model to estimate future revenue.

The forecasting pipeline includes:

* Monthly revenue aggregation
* Time trend modeling
* Seasonal encoding using month features
* Linear regression prediction for future periods

---

## Technology Stack

* Python
* Streamlit
* Pandas
* NumPy
* Plotly
* Scikit-learn

The application uses a modular architecture where analytics functions are separated into dedicated modules (`src/`).



---

## Installation

Clone the repository:

```
git clone https://github.com/Lidia-KH/sales-dashboard.git
cd sales-dashboard
```

Install dependencies:

```
pip install -r requirements.txt
```

Run the application:

```
streamlit run app.py
```

---

## Dataset Format

The dashboard accepts any dataset containing the following columns:

Required fields:

* date
* product
* customer_id
* quantity
* unit_price

Optional fields:

* unit_cost
* traffic_source
* marketing_spend
* inventory

If revenue is not present, it is automatically computed as:

```
revenue = quantity × unit_price
```

---

## Example Use Cases

* E-commerce analytics
* Retail sales monitoring
* Marketing campaign evaluation
* Inventory management
* Revenue forecasting

---

## Future Improvements

Potential enhancements include:

* Machine learning forecasting models (LSTM, Transformer)
* Marketing ROI prediction
* Customer segmentation
* Automated anomaly detection
* Multi-store analytics support

---

## License

This project is released under the MIT License.
