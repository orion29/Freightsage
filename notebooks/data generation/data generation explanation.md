# Logistics Mock Data Generator Script Description

## Purpose
This Python script generates a realistic mock dataset representing logistics shipments originating from Gurugram, India. The data is designed to simulate key aspects of logistics operations, costs, and timelines, incorporating variations, complexities, and potential issues found in real-world supply chains. The generated data is specifically structured to support various AI/ML use cases for logistics analysis, prediction, optimization, and alerting.

## Dependencies
The script requires the following Python libraries:
- pandas
- numpy
- datetime
- random

## Core Functionality & Data Generation Logic
The script generates data row by row (simulating individual shipments) based on predefined configurations and probabilistic choices, incorporating domain knowledge to create realistic relationships:

1.  **Configuration:** Sets constants like the number of rows, date range, origin details, lists of destinations, product categories, shipment modes, transporters, customer IDs, service levels, and packaging types.
2.  **Routes:** Defines multiple potential physical routes for select origin-destination pairs, each with specific distances, estimated travel times, and complexity factors. International destinations are simplified as single routes but with mode-specific international transit times.
3.  **Shipment Attributes:** For each shipment, it randomly selects:
    * An Order Date and Shipment Date (a few days after the order).
    * A Destination City/Country from the defined list (weighted to simulate higher traffic routes).
    * One specific Route from the available options for the chosen OD pair.
    * A Customer ID.
    * A Service Level (Standard, Express, Critical).
    * A Product Category and Product ID (with associated weight, volume, and value ranges).
    * A Packaging Type.
    * Calculates Line Item Quantity, Unit Price, Pack Price, and Line Item Value.
    * Calculates total Weight and Volume for the shipment.
4.  **Mode & Transporter Selection:** Based on the shipment attributes (distance, weight/volume, service level, content type) and the chosen route, it selects a suitable Shipment Mode and a Transporter that operates in that mode. Transporter selection is influenced by a simulated "Carrier Product Fit Score" based on predefined domain knowledge.
5.  **Billable Weight:** Calculates billable weight (max of actual weight and volumetric weight) using mode-specific volumetric factors, reflecting carrier pricing practices.
6.  **Freight Cost Calculation (Proposed vs. Actual):**
    * **Proposed Cost:** Calculates an initial quote based on the chosen route's distance, billable weight, mode, transporter's base rate modifier, fixed fees, weight slab pricing, and a standard fuel surcharge. Includes minor noise.
    * **Actual Cost:** Starts with the proposed cost and adds variations based on: actual (variable) fuel surcharge (influenced by route deviation), potential unexpected surcharges (influenced by route complexity, content type, and seasonality), and a market-wide seasonal cost factor. Deliberate cost outliers are also introduced randomly.
    * Calculates Price Variance ($ and %).
    * Calculates Cost Per Billable Kg.
7.  **Delivery Time Calculation (Expected vs. Actual):**
    * **Expected Time:** Calculated based on the chosen route's estimated travel time, adjusted by the selected mode's base speed, the transporter's speed modifier, and the requested service level. Includes a base handling time and is influenced by the route's base complexity.
    * **Actual Time:** Simulated based on the chosen route's distance and a simulated `Avg Speed` (influenced by mode speed, route complexity, congestion, and weather), plus simulated `Halt Duration`, `Customs/Border Delay`, and variable handling time. Deliberate operational delays are also added randomly, influenced by seasonality.
    * Calculates Delay (Actual - Expected).
    * Calculates Actual Delivery Date from Shipment Date and Actual Delivery Time.
8.  **Simulated Operational/GPS Data:** Generates values for columns like `Avg Speed`, `Halt Duration`, `Route Deviation Factor`, `Weather Impact`, `Customs/Border Delay`. The values for these are influenced by the chosen route's characteristics, complexity, and seasonal/monthly congestion patterns.
9.  **Derived Metrics & Flags:** Calculates `Status` (Delivered, Delayed, Early), `On-Time Delivery`, `Cost Outlier`, `Packaging Efficiency`, and `Carbon Emissions (kg CO2)`.
10. **Temporal Features:** Extracts `Shipment Month` and `Shipment Day of Week`.
11. **Transporter Performance History:** *After* generating all shipments, calculates aggregate historical performance metrics per transporter (Avg Delay, On-Time %, Avg Price Variance %, Reliability Score) from the generated data and adds these as columns to each row for reference.

## What it Generates
The script generates a pandas DataFrame with 10,000 rows and numerous columns (see column description below) covering:
- Shipment identifiers and dates
- Origin and Destination details (including specific route taken)
- Product and Line Item details (quantity, value, type, packaging)
- Weight and Volume metrics (including billable weight)
- Shipment Mode and Transporter chosen (with a Carrier Product Fit Score)
- Expected and Actual Delivery Times and Delay
- Simulated "real-world" factors impacting transit (speed, halts, deviation, weather, customs, route congestion)
- Proposed and Actual Freight Costs, including variance analysis and outlier flags
- Calculated metrics like Cost Per Billable Kg and Carbon Emissions
- Aggregated Transporter Performance scores

## How it Supports AI Use Cases
The diverse range of columns, realistic (non-random) relationships between them, simulated operational noise, and included anomalies (delays, cost spikes, price variances, route differences, seasonality) make this data suitable for training and demonstrating the AI functionalities:
- **Prediction:** Regression models for `Delivery Time`, `Delay`, `Actual Freight Cost`. Classification for `On-Time Delivery`, `Status`, `Cost Outlier`.
- **Estimation:** Estimating `Actual Freight Cost` based on shipment attributes.
- **Optimization:** Identifying cost-optimal `Transporter Name` and `Chosen Route Name` for specific OD pairs, `Shipment Modes`, and `Product Categories` based on `Actual Freight Cost` and performance metrics. Optimizing `Packaging Efficiency` or reducing `Carbon Emissions`.
- **Profiling:** Building `Transporter Performance History` profiles. Analyzing route reliability based on `Delay`, `Halt Duration`, `Route Congestion Factor`.
- **Alerting:** Detecting anomalies in `Actual Freight Cost`, `Delay`, or `Price Variance (%)` over time (`Smart Alerts`).
- **Recommendations:** Recommending carriers/routes based on integrated cost, time, reliability, and specialization data.

## Customization
Users can modify the script to:
- Change `NUM_ROWS`, `START_DATE`, `END_DATE`.
- Add/modify destinations, routes (including their distances, times, and complexities).
- Add/modify product categories, modes, transporters, customer IDs.
- Adjust weight slabs, volumetric factors, base cost/speed parameters.
- Refine seasonal factors and route congestion patterns based on more specific knowledge.
- Modify the logic for generating noise, delays, surcharges, and outliers to match observed patterns in real data.
- Adjust the calculation or weighting of the `Transporter Performance` and `Carrier Product Fit` scores.