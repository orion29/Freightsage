import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set a seed for reproducibility
np.random.seed(42)
random.seed(42)

# --- Configuration ---
NUM_ROWS = 10000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)
ORIGIN_CITY = 'Gurugram'
ORIGIN_COUNTRY = 'India'
MANUFACTURING_SITE = 'Gurugram Mfg Hub'

# Define MULTIPLE possible routes for select origin-destination pairs
# Each route option: (Origin City, Destination City, Route Name, Distance (km), Estimated Travel Time (hours), Route Complexity Factor)
# Complexity Factor (1.0 = standard, > 1.0 = slower/more prone to delays)
routes = [
    ('Gurugram', 'Mumbai', 'NH 48 Direct', 1400, 28, 1.1), # Standard highway route
    ('Gurugram', 'Mumbai', 'Via Jaipur-Udaipur', 1450, 30, 1.2), # Slightly longer, potentially congested sections
    ('Gurugram', 'Mumbai', 'Via Agra-Indore', 1500, 32, 1.3), # Longer, more complex
    ('Gurugram', 'Chennai', 'NH 44 South', 2200, 40, 1.2), # Primary south route
    ('Gurugram', 'Chennai', 'East Coast detour', 2350, 45, 1.4), # Longer, potentially slower
    ('Gurugram', 'Bangalore', 'NH 44 Standard', 2150, 38, 1.1), # Primary route
    ('Gurugram', 'Bangalore', 'Western Bypass', 2200, 40, 1.2), # Alternative
    ('Gurugram', 'Kolkata', 'NH 19 East', 1500, 30, 1.0), # Relatively standard
    ('Gurugram', 'Pune', 'Standard Route', 1450, 29, 1.0),
    ('Gurugram', 'Ahmedabad', 'NH 48 West', 800, 14, 1.0),
    ('Gurugram', 'Jaipur', 'NH 48 Short', 300, 5, 1.0),
    # International destinations - simplified as single "routes" but with mode-specific times and complexities
    ('Gurugram', 'New York', 'Air/Sea Route NY', 12000, {'Air Cargo': 120, 'Sea': 720, 'Express Air': 72}, 1.3), # Time in hours, different per mode
    ('Gurugram', 'Los Angeles', 'Air/Sea Route LA', 13500, {'Air Cargo': 130, 'Sea': 750, 'Express Air': 78}, 1.3),
    ('Gurugram', 'Frankfurt', 'Air/Sea Route FRA', 6500, {'Air Cargo': 80, 'Sea': 500, 'Express Air': 48}, 1.1),
    ('Gurugram', 'London', 'Air/Sea Route LDN', 6700, {'Air Cargo': 85, 'Sea': 520, 'Express Air': 50}, 1.2),
    ('Gurugram', 'Dubai', 'Air/Sea Route DXB', 2200, {'Air Cargo': 24, 'Sea': 120, 'Express Air': 18}, 1.0),
    ('Gurugram', 'Singapore', 'Air/Sea Route SIN', 4000, {'Air Cargo': 48, 'Sea': 200, 'Express Air': 30}, 1.0),
    ('Gurugram', 'Sydney', 'Air/Sea Route SYD', 10000, {'Air Cargo': 150, 'Sea': 600, 'Express Air': 96}, 1.4),
    ('Gurugram', 'Shanghai', 'Air/Sea Route SHA', 4500, {'Air Cargo': 55, 'Sea': 250, 'Express Air': 36}, 1.2),
    ('Gurugram', 'Tokyo', 'Air/Sea Route TYO', 5800, {'Air Cargo': 70, 'Sea': 300, 'Express Air': 42}, 1.1),
    ('Gurugram', 'Toronto', 'Air/Sea Route YYZ', 11500, {'Air Cargo': 125, 'Sea': 700, 'Express Air': 75}, 1.3),
]

# Map Origin-Destination pairs to available routes
route_options = {}
for org, dest, name, dist, time, complexity in routes:
    if (org, dest) not in route_options:
        route_options[(org, dest)] = []
    route_options[(org, dest)].append({'Route Name': name, 'Distance (km)': dist, 'Estimated Travel Time (hours)': time, 'Route Complexity Factor': complexity})

# List of unique origin-destination pairs
od_pairs = list(route_options.keys())

# Product categories (Same as before)
product_categories = {
    'Electronics': {'weight_per_unit': (0.1, 5), 'volume_per_unit': (0.001, 0.05), 'value_per_unit': (100, 5000), 'content_type': 'Fragile'},
    'Pharma': {'weight_per_unit': (0.05, 2), 'volume_per_unit': (0.0005, 0.02), 'value_per_unit': (50, 2000), 'content_type': 'Temperature Controlled'},
    'Textiles': {'weight_per_unit': (0.2, 10), 'volume_per_unit': (0.005, 0.1), 'value_per_unit': (10, 500), 'content_type': 'General Goods'},
    'Machinery Parts': {'weight_per_unit': (5, 500), 'volume_per_unit': (0.05, 5), 'value_per_unit': (500, 10000), 'content_type': 'Heavy/Bulky'},
    'Consumer Goods': {'weight_per_unit': (0.5, 15), 'volume_per_unit': (0.01, 0.2), 'value_per_unit': (20, 300), 'content_type': 'General Goods'},
    'Hazardous Materials': {'weight_per_unit': (1, 200), 'volume_per_unit': (0.01, 1), 'value_per_unit': (100, 5000), 'content_type': 'Hazardous'},
}
product_ids = [f'PROD{i:04d}' for i in range(1, len(product_categories) * 20 + 1)]

# Shipment modes (Speed base in kph, Cost base per 100km per kg base)
shipment_modes = {
    'Road': {'speed_base_kph': 40, 'cost_per_100km_per_kg_base': 0.5, 'fixed_fee': 20, 'distance_limit': 3000},
    'Rail': {'speed_base_kph': 30, 'cost_per_100km_per_kg_base': 0.4, 'fixed_fee': 30, 'distance_limit': 3000},
    'Air Cargo': {'speed_base_kph': 700, 'cost_per_100km_per_kg_base': 3.0, 'fixed_fee': 100, 'distance_limit': 20000},
    'Sea': {'speed_base_kph': 25, 'cost_per_100km_per_kg_base': 0.1, 'fixed_fee': 150, 'distance_limit': 30000},
    'Express Air': {'speed_base_kph': 1000, 'cost_per_100km_per_kg_base': 5.0, 'fixed_fee': 50, 'distance_limit': 20000},
    'Express Road': {'speed_base_kph': 50, 'cost_per_100km_per_kg_base': 0.8, 'fixed_fee': 30, 'distance_limit': 1500},
}

# Volumetric weight factor (Same as before)
volumetric_factors = {
    'Road': 250, 'Rail': 200, 'Air Cargo': 167, 'Sea': 1000, 'Express Air': 200, 'Express Road': 250,
}

# Weight slabs (Same as before)
weight_slabs = [
    (0, 5, 2.0), (5, 10, 1.5), (10, 25, 1.2), (25, 100, 1.0), (100, 500, 0.8), (500, np.inf, 0.6),
]

# Define transporters (Vendors) and their profiles (Same as before)
transporters = {
    'Blue Dart': {'modes': ['Air Cargo', 'Express Air', 'Road', 'Express Road'], 'cost_mod': 1.1, 'speed_mod': 1.2, 'focus': 'Domestic/Premium'},
    'Delhivery': {'modes': ['Air Cargo', 'Express Air', 'Road', 'Express Road'], 'cost_mod': 0.95, 'speed_mod': 1.0, 'focus': 'Domestic/WideNetwork'},
    'Safeexpress': {'modes': ['Road', 'Rail'], 'cost_mod': 0.9, 'speed_mod': 0.9, 'focus': 'Domestic/Surface'},
    'Gati': {'modes': ['Road', 'Air Cargo'], 'cost_mod': 1.0, 'speed_mod': 1.05, 'focus': 'Domestic/Integrated'},
    'DHL': {'modes': ['Air Cargo', 'Express Air'], 'cost_mod': 1.3, 'speed_mod': 1.3, 'focus': 'International/Premium'},
    'FedEx': {'modes': ['Air Cargo', 'Express Air'], 'cost_mod': 1.25, 'speed_mod': 1.25, 'focus': 'International/Premium'},
    'Maersk': {'modes': ['Sea'], 'cost_mod': 0.85, 'speed_mod': 0.8, 'focus': 'International/Sea'},
    'MSC': {'modes': ['Sea'], 'cost_mod': 0.88, 'speed_mod': 0.82, 'focus': 'International/Sea'},
    'Local Carriers': {'modes': ['Road'], 'cost_mod': 0.7, 'speed_mod': 0.8, 'focus': 'Domestic/Local/Budget'},
}

# Customer IDs (Same as before)
customer_ids = [f'CUST{i:03d}' for i in range(1, 51)]

# Service Levels (Same as before)
service_levels = ['Standard', 'Express', 'Critical']
service_level_speed_mod = {'Standard': 1.0, 'Express': 1.2, 'Critical': 1.5}

# Packaging Types and a rough estimate of volume capacity per unit of packaging (m^3 per unit)
packaging_types = {
    'Box': 0.1, # Avg volume of a box
    'Pallet': 1.5, # Avg volume on a pallet
    'Crate': 2.0, # Avg volume in a crate
    'Carton': 0.05, # Avg volume of a carton
    'Loose': 0.0, # No standard packaging volume
}


# Weather Impacts (Same as before)
weather_impacts = ['None', 'Minor Rain/Fog', 'Moderate Rain/Fog', 'Severe Weather']
weather_speed_mod = {'None': 1.0, 'Minor Rain/Fog': 0.98, 'Moderate Rain/Fog': 0.9, 'Severe Weather': 0.7}

# Domain Knowledge: Carrier Specialization Scores (Higher is better fit/performance for this product)
# Score 1-10. Influences chance of selecting this carrier for this product type and potentially cost/speed modifiers.
carrier_product_specialization = {
    'Blue Dart': {'Electronics': 9, 'Pharma': 8, 'Textiles': 6, 'Machinery Parts': 5, 'Consumer Goods': 8, 'Hazardous Materials': 4},
    'Delhivery': {'Electronics': 8, 'Pharma': 7, 'Textiles': 7, 'Machinery Parts': 6, 'Consumer Goods': 9, 'Hazardous Materials': 5},
    'Safeexpress': {'Electronics': 5, 'Pharma': 6, 'Textiles': 9, 'Machinery Parts': 8, 'Consumer Goods': 7, 'Hazardous Materials': 7},
    'Gati': {'Electronics': 7, 'Pharma': 6, 'Textiles': 8, 'Machinery Parts': 7, 'Consumer Goods': 8, 'Hazardous Materials': 6},
    'DHL': {'Electronics': 10, 'Pharma': 9, 'Textiles': 7, 'Machinery Parts': 6, 'Consumer Goods': 8, 'Hazardous Materials': 5},
    'FedEx': {'Electronics': 9, 'Pharma': 9, 'Textiles': 7, 'Machinery Parts': 6, 'Consumer Goods': 8, 'Hazardous Materials': 5},
    'Maersk': {'Electronics': 4, 'Pharma': 5, 'Textiles': 10, 'Machinery Parts': 9, 'Consumer Goods': 6, 'Hazardous Materials': 8},
    'MSC': {'Electronics': 4, 'Pharma': 5, 'Textiles': 10, 'Machinery Parts': 9, 'Consumer Goods': 6, 'Hazardous Materials': 8},
    'Local Carriers': {'Electronics': 5, 'Pharma': 5, 'Textiles': 7, 'Machinery Parts': 6, 'Consumer Goods': 7, 'Hazardous Materials': 6},
}

# Domain Knowledge: Seasonal Factors (Cost and Delay multipliers by month)
# Cost Factors: Increase during peak season (Oct-Dec), slightly during monsoon (July-Aug)
# Delay Factors: Increase during peak season, significantly during monsoon, maybe slightly Jan (fog)
seasonal_factors = {
    1: {'cost': 1.05, 'delay': 1.1},  # Jan - slight cost increase, more delays (fog)
    2: {'cost': 1.0, 'delay': 1.0},
    3: {'cost': 1.0, 'delay': 1.0},
    4: {'cost': 0.98, 'delay': 0.95},
    5: {'cost': 0.95, 'delay': 0.95},
    6: {'cost': 1.0, 'delay': 1.05},  # Monsoon begins
    7: {'cost': 1.08, 'delay': 1.25}, # Monsoon peak - higher costs, significant delays
    8: {'cost': 1.05, 'delay': 1.15}, # Monsoon winding down
    9: {'cost': 1.0, 'delay': 1.0},
    10: {'cost': 1.1, 'delay': 1.05}, # Festival season begins - higher costs, slight delays
    11: {'cost': 1.2, 'delay': 1.15}, # Peak festival season - highest costs, more delays
    12: {'cost': 1.15, 'delay': 1.1}, # Year-end rush
}

# Domain Knowledge: Route Congestion Patterns (Multiplier on delay/halt chance based on route and month)
# Example: Higher congestion on major routes during festival season (Oct-Dec)
route_congestion_patterns = {}
for org, dest, name, dist, time, complexity in routes:
     base_factor = complexity # Start with base complexity from route definition
     monthly_factors = [base_factor] * 12 # Default to base complexity
     # Add specific congestion for domestic routes during peak season/monsoon
     if org == dest: # Domestic routes
         if 'NH 48' in name or 'NH 44' in name: # Major national highways
              monthly_factors[6] *= 1.2 # July monsoon
              monthly_factors[7] *= 1.3 # Aug monsoon
              monthly_factors[9] *= 1.2 # Oct festival start
              monthly_factors[10] *= 1.4 # Nov peak festival
              monthly_factors[11] *= 1.3 # Dec festival end / year end
         elif 'Via' in name or 'detour' in name: # Alternative/complex routes
              monthly_factors[6] *= 1.3 # Monsoon
              monthly_factors[7] *= 1.4 # Monsoon
              monthly_factors[9] *= 1.1 # Festival
              monthly_factors[10] *= 1.2 # Festival
     route_congestion_patterns[name] = monthly_factors

# Emissions factors (kg CO2 per ton-km) - General estimates
emissions_factors = {
    'Road': 0.06,
    'Rail': 0.02,
    'Air Cargo': 0.8,
    'Sea': 0.01,
    'Express Air': 1.0, # Higher for urgent/less efficient air
    'Express Road': 0.07, # Slightly higher for faster road
}

# --- Data Generation ---

data = []

for i in range(NUM_ROWS):
    shipment_id = f'SHIP{i+1:05d}'
    order_date = START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days))
    shipment_date = order_date + timedelta(days=random.randint(0, 3)) # Ship 0-3 days after order
    shipment_month = shipment_date.month
    shipment_day_of_week = shipment_date.weekday() 

    origin_city = ORIGIN_CITY
    origin_country = ORIGIN_COUNTRY
    manufacturing_site = MANUFACTURING_SITE

    # Select an Origin-Destination pair
    od_pair = random.choices(od_pairs, weights=[10, 8, 8, 6, 7, 5, 4, # Domestic weights
                                               5, 4, 6, 6, 9, 5, 3, 4, 3, 2], k=1)[0] # International weights
    dest_country = next(item[0] for item in routes if (item[0], item[1]) == od_pair)
    dest_city = od_pair[1]

    # Select one of the possible routes for this OD pair
    chosen_route = random.choice(route_options[od_pair])
    route_name = chosen_route['Route Name']
    distance_km = chosen_route['Distance (km)']
    route_estimated_travel_time_hours_base = chosen_route['Estimated Travel Time (hours)']
    route_complexity_factor_base = chosen_route['Route Complexity Factor']

    # Get route congestion factor for this month
    route_congestion_factor_monthly = route_congestion_patterns[route_name][shipment_month-1]


    customer_id = random.choice(customer_ids)
    service_level = random.choices(service_levels, weights=[0.7, 0.2, 0.1], k=1)[0]

    # Select product category and ID
    product_category = random.choices(list(product_categories.keys()), weights=[10, 8, 12, 5, 15, 1], k=1)[0]
    cat_index = list(product_categories.keys()).index(product_category)
    product_id = random.choice(product_ids[cat_index*20 : (cat_index+1)*20])
    shipment_content_type = product_categories[product_category]['content_type']

    line_item_quantity = random.randint(1, 500 if product_category not in ['Machinery Parts', 'Hazardous Materials'] else 20)
    unit_price = round(random.uniform(*product_categories[product_category]['value_per_unit']), 2)
    pack_price = round(unit_price * random.uniform(0.98, 1.02), 2)
    line_item_value_usd = round(line_item_quantity * unit_price, 2)

    weight_kg = round(line_item_quantity * random.uniform(*product_categories[product_category]['weight_per_unit']), 2)
    volume_m3 = round(line_item_quantity * random.uniform(*product_categories[product_category]['volume_per_unit']), 3)

    # Packaging Type and efficiency calculation
    packaging_type = random.choices(list(packaging_types.keys()), weights=[4, 3, 1, 4, 2], k=1)[0]
    packaging_standard_vol_per_unit = packaging_types[packaging_type]
    # Avoid division by zero or if packaging type has no standard volume (like 'Loose')
    if packaging_standard_vol_per_unit > 0 and line_item_quantity > 0:
         packaging_efficiency = round(volume_m3 / (packaging_standard_vol_per_unit * line_item_quantity), 2)
    else:
         packaging_efficiency = 1.0 # Assume perfect efficiency or not applicable

    # Select Shipment Mode appropriate for distance, weight/volume, service level, content type, AND the chosen route
    available_modes = [mode for mode, details in shipment_modes.items() if distance_km <= details['distance_limit']]

    # Filter modes based on content type and service level (Same as before)
    if 'Hazardous' in shipment_content_type:
        available_modes = [m for m in available_modes if m in ['Road', 'Sea', 'Air Cargo']]
    if 'Temperature Controlled' in shipment_content_type:
        available_modes = [m for m in available_modes if m in ['Air Cargo', 'Express Air', 'Road']]
    if service_level in ['Express', 'Critical']:
        available_modes = [m for m in available_modes if 'Express' in m or 'Air' in m or (m == 'Road' and distance_km < 1000)]

    # Filter based on route type (Domestic/International) (Same as before)
    if od_pair[0] == od_pair[1]: # Domestic route
         available_modes = [m for m in available_modes if m in ['Road', 'Rail', 'Air Cargo', 'Express Road', 'Express Air']]
    else: # International route
         available_modes = [m for m in available_modes if m in ['Air Cargo', 'Sea', 'Express Air']]

    # Prefer modes based on weight/volume if multiple suitable modes remain (Same as before)
    if len(available_modes) > 1:
         if weight_kg > 500 or volume_m3 > 3:
             available_modes = [m for m in available_modes if m in ['Road', 'Rail', 'Sea'] and m in available_modes]
         elif weight_kg < 10 or volume_m3 < 0.1 and service_level in ['Express', 'Critical']:
             available_modes = [m for m in available_modes if ('Express' in m or 'Air' in m) and m in available_modes]

    # Fallback if filtering was too aggressive
    if not available_modes:
         selected_mode = 'Road' if distance_km < 1500 else 'Air Cargo'
    else:
         # Select Transporter that operates in the selected mode and destination type
         # Get available transporters for modes
         potential_transporters = [t_name for t_name, t_details in transporters.items() if any(mode in available_modes for mode in t_details['modes'])]

         # Refine based on destination type focus
         if dest_country == 'India':
             potential_transporters = [t for t in potential_transporters if 'Domestic' in transporters[t]['focus']]
         else: # International
              potential_transporters = [t for t in potential_transporters if 'International' in transporters[t]['focus']]

         # Use Carrier Product Fit Score to influence selection probability
         if potential_transporters:
             # Calculate a weighted score for each potential transporter based on mode fit and product fit
             transporter_selection_weights = []
             for t_name in potential_transporters:
                 # Base weight + bonus if mode is preferred + bonus based on product fit
                 weight = 1.0
                 if selected_mode in transporters[t_name]['modes']: # Should always be true due to filtering, but safety
                     weight *= 1.5 # Prefer carriers that explicitly list the mode
                 product_fit_score = carrier_product_specialization.get(t_name, {}).get(product_category, 5) # Default score 5
                 weight *= (product_fit_score / 5.0) # Scale product fit score to influence weight (e.g., score 10 is 2x weight)
                 transporter_selection_weights.append(weight)

             selected_transporter = random.choices(potential_transporters, weights=transporter_selection_weights, k=1)[0]
             # Now that transporter is selected, ensure the mode they use is valid. Re-select mode if the chosen transporter doesn't support the ideal modes.
             transporter_supported_modes = [m for m in available_modes if m in transporters[selected_transporter]['modes']]
             if not transporter_supported_modes:
                 # Fallback: transporter doesn't support any of the initially preferred modes for this shipment.
                 # This shouldn't happen if filtering is correct, but as a safety, pick the mode most common for the transporter/route.
                 selected_mode = random.choice(transporters[selected_transporter]['modes'])
             else:
                 selected_mode = random.choice(transporter_supported_modes) # Pick one of the valid modes the chosen transporter supports
         else:
              # Extreme fallback - no suitable transporter found, pick random mode/transporter (should be rare)
              selected_transporter = random.choice(list(transporters.keys()))
              selected_mode = random.choice(transporters[selected_transporter]['modes'])


    carrier_product_fit_score = carrier_product_specialization.get(selected_transporter, {}).get(product_category, 5)


    # Calculate Billable Weight (Same as before)
    volumetric_weight_kg = volume_m3 * volumetric_factors.get(selected_mode, 200)
    billable_weight_kg = max(weight_kg, volumetric_weight_kg)


    # --- Calculate Proposed Freight Cost (USD) ---
    base_rate_per_100km_per_kg = shipment_modes[selected_mode]['cost_per_100km_per_kg_base']
    weight_slab_multiplier = 1.0
    for low, high, multiplier in weight_slabs:
        if billable_weight_kg >= low and billable_weight_kg < high:
            weight_slab_multiplier = multiplier
            break

    distance_cost_proposed = (distance_km / 100) * base_rate_per_100km_per_kg * billable_weight_kg * weight_slab_multiplier
    fixed_fee_proposed = shipment_modes[selected_mode]['fixed_fee']
    transporter_cost_modifier_proposed = transporters[selected_transporter].get('cost_mod', 1.0)
    proposed_freight_cost_usd = (distance_cost_proposed + fixed_fee_proposed) * transporter_cost_modifier_proposed

    standard_fuel_surcharge_rate = 0.20
    proposed_fuel_surcharge = distance_cost_proposed * standard_fuel_surcharge_rate
    proposed_freight_cost_usd += proposed_fuel_surcharge

    min_charge = 50 if distance_km < 1000 else 100
    proposed_freight_cost_usd = max(proposed_freight_cost_usd, min_charge)

    proposed_cost_noise_percent = random.uniform(-0.01, 0.01)
    proposed_freight_cost_usd += proposed_freight_cost_usd * proposed_cost_noise_percent
    proposed_freight_cost_usd = max(10, round(proposed_freight_cost_usd, 2))


    # --- Calculate Expected Delivery Time (Days) ---
    transporter_speed_modifier = transporters[selected_transporter].get('speed_mod', 1.0)
    service_level_modifier = service_level_speed_mod[service_level]

    if isinstance(route_estimated_travel_time_hours_base, dict):
         route_est_time_hours = route_estimated_travel_time_hours_base.get(selected_mode, 9999)
    else:
         route_est_time_hours = route_estimated_travel_time_hours_base

    expected_delivery_time_hours = route_est_time_hours / (transporter_speed_modifier * service_level_modifier)
    expected_delivery_time_hours += random.uniform(12, 36) # Add handling/loading/transfer time
    expected_delivery_time_hours *= route_complexity_factor_base # Base route complexity impacts expected time

    expected_delivery_time_days = max(1, round(expected_delivery_time_hours / 24, 1))


    # --- Simulate GPS-derived factors and calculate Actual Delivery Time & Actual Freight Cost ---
    base_mode_speed_kph = shipment_modes[selected_mode]['speed_base_kph']
    avg_speed_kmph = base_mode_speed_kph * random.uniform(0.8, 1.2)
    weather_impact = random.choices(weather_impacts, weights=[0.7, 0.2, 0.07, 0.03], k=1)[0]
    avg_speed_kmph *= weather_speed_mod[weather_impact]
    # Avg speed also impacted by route complexity and congestion
    avg_speed_kmph /= (route_complexity_factor_base * route_congestion_factor_monthly)


    route_deviation_factor = random.uniform(1.0, 1.1)
    route_deviation_factor *= (route_complexity_factor_base * route_congestion_factor_monthly) # Deviation increased by complexity & congestion

    halt_duration_hours = (distance_km / 100) * random.uniform(0.1, 0.5)
    if selected_mode in ['Air Cargo', 'Sea', 'Express Air']: halt_duration_hours *= 0.5
    halt_duration_hours *= (route_complexity_factor_base * route_congestion_factor_monthly) # Halts increased by complexity & congestion
    if weather_impact in ['Moderate Rain/Fog', 'Severe Weather']: halt_duration_hours += random.uniform(1, 10)
    halt_duration_hours = round(max(0, halt_duration_hours), 1)

    customs_border_delay_hours = 0
    if dest_country != 'India':
        # Higher chance/magnitude based on complexity and potential seasonal/congestion impact on borders
        delay_chance = 0.3 + (route_complexity_factor_base - 1.0) * 0.5 + (route_congestion_factor_monthly - route_complexity_factor_base) * 0.3
        if random.random() < min(0.8, delay_chance): # Cap chance at 80%
            customs_border_delay_hours = random.uniform(1, 72)
            customs_border_delay_hours *= (route_complexity_factor_base * (1 + (route_congestion_factor_monthly - route_complexity_factor_base)*0.5)) # Magnitude increased by complexity/congestion
    customs_border_delay_hours = round(customs_border_delay_hours, 1)

    actual_handling_time_hours = random.uniform(10, 40)

    effective_distance_km = distance_km * route_deviation_factor
    travel_time_hours_actual = (effective_distance_km / avg_speed_kmph) if avg_speed_kmph > 0 else 9999

    actual_total_time_hours = travel_time_hours_actual + halt_duration_hours + customs_border_delay_hours + actual_handling_time_hours

    # Apply seasonal delay factor
    actual_total_time_hours *= seasonal_factors[shipment_month]['delay']

    actual_delivery_time_days = round(actual_total_time_hours / 24, 1)
    actual_delivery_time_days = max(1, actual_delivery_time_days)

    # Introduce additional random operational delays (Same as before)
    if random.random() < 0.05 * seasonal_factors[shipment_month]['delay']: # Chance slightly increased during high delay months
         actual_delivery_time_days += random.uniform(1, 5)


    # Calculate Delay
    delay_days = round(actual_delivery_time_days - expected_delivery_time_days, 1)

    # Calculate Actual Delivery Date
    actual_delivery_date = shipment_date + timedelta(days=int(round(actual_delivery_time_days)))


    # --- Calculate Actual Freight Cost (USD) ---
    actual_freight_cost_usd = proposed_freight_cost_usd

    # Apply variable fuel surcharge based on actual factors (e.g., route deviation, seasonal fuel price)
    actual_fuel_surcharge_rate = random.uniform(0.18, 0.28)
    actual_fuel_surcharge = distance_cost_proposed * actual_fuel_surcharge_rate # Apply rate to base distance cost
    actual_fuel_surcharge *= route_deviation_factor # Adjust slightly based on route deviation
    actual_freight_cost_usd += (actual_fuel_surcharge - proposed_fuel_surcharge)

    # Add potential surcharges not included in the quote
    unexpected_surcharges = 0
    if random.random() < 0.15 * seasonal_factors[shipment_month]['cost']: # Higher chance during peak season
        unexpected_surcharges = random.uniform(10, 150) # Base unexpected fee
        if route_complexity_factor_base > 1.2: unexpected_surcharges *= random.uniform(1.0, 1.5)
        if shipment_content_type in ['Hazardous Materials', 'Temperature Controlled']: unexpected_surcharges *= random.uniform(1.0, 1.3)
        unexpected_surcharges *= seasonal_factors[shipment_month]['cost'] # Seasonal impact on surcharges

    actual_freight_cost_usd += unexpected_surcharges

    # Apply seasonal cost factor to the whole cost (reflects overall market conditions)
    actual_freight_cost_usd *= seasonal_factors[shipment_month]['cost']


    # Introduce deliberate cost outliers (Same as before, apply as a final spike)
    is_cost_outlier = False
    if random.random() < 0.02:
         spike_amount = random.uniform(0.8 * actual_freight_cost_usd, 3.0 * actual_freight_cost_usd)
         actual_freight_cost_usd += spike_amount
         is_cost_outlier = True

    actual_freight_cost_usd = max(10, round(actual_freight_cost_usd, 2))

    # Calculate derived metrics
    cost_per_billable_kg_usd = round(actual_freight_cost_usd / billable_weight_kg if billable_weight_kg > 0 else 0, 2)
    price_variance_usd = round(actual_freight_cost_usd - proposed_freight_cost_usd, 2)
    price_variance_percent = round((price_variance_usd / proposed_freight_cost_usd) * 100 if proposed_freight_cost_usd > 0 else 0, 2)

    # Determine Status (Same as before)
    status = 'Delivered'
    if delay_days > 0.5:
        status = 'Delayed'
    elif delay_days < -0.5:
        status = 'Early'
    on_time_delivery = 'Yes' if status != 'Delayed' else 'No'

    # Calculate Carbon Emissions (kg CO2)
    # Emissions = Distance (km) * (Weight in tonnes) * Emission Factor (kg CO2 / ton-km) * Route Deviation Factor (approx)
    # Use Billable Weight as it's closer to the 'load' the vehicle carries
    weight_tonnes = billable_weight_kg / 1000
    emissions_factor = emissions_factors.get(selected_mode, 0.05) # Default factor
    carbon_emissions_kg_co2 = distance_km * weight_tonnes * emissions_factor * route_deviation_factor # Deviation means more distance/fuel
    carbon_emissions_kg_co2 = round(max(0, carbon_emissions_kg_co2), 2)


    data.append({
        'Shipment ID': shipment_id,
        'Order Date': order_date,
        'Shipment Date': shipment_date,
        'Actual Delivery Date': actual_delivery_date,
        'Origin City': origin_city,
        'Origin Country': origin_country,
        'Manufacturing Site': manufacturing_site,
        'Destination Country': dest_country,
        'Destination City': dest_city,
        'Chosen Route Name': route_name,
        'Distance (km)': distance_km,
        'Customer ID': customer_id,
        'Service Level': service_level,
        'Product ID': product_id,
        'Product Category': product_category,
        'Shipment Content Type': shipment_content_type,
        'Packaging Type': packaging_type,
        'Packaging Efficiency': packaging_efficiency, # Added
        'Line Item Quantity': line_item_quantity,
        'Unit Price (USD)': unit_price,
        'Pack Price (USD)': pack_price,
        'Line Item Value (USD)': line_item_value_usd,
        'Weight (kg)': weight_kg,
        'Volume (m³)': volume_m3,
        'Billable Weight (kg)': billable_weight_kg,
        'Shipment Mode': selected_mode,
        'Transporter Name': selected_transporter,
        'Carrier Product Fit Score': carrier_product_fit_score, # Added
        'Expected Delivery Time (Days)': expected_delivery_time_days,
        'Delivery Time (Days)': actual_delivery_time_days,
        'Delay (Days)': delay_days,
        'Avg Speed (km/h)': round(avg_speed_kmph, 1),
        'Halt Duration (hours)': halt_duration_hours,
        'Route Deviation Factor': round(route_deviation_factor, 2),
        'Weather Impact': weather_impact,
        'Customs/Border Delay (hours)': customs_border_delay_hours,
        'Route Congestion Factor': round(route_congestion_factor_monthly, 2), # Added
        'Seasonal Cost Factor': seasonal_factors[shipment_month]['cost'], # Added (for reference)
        'Seasonal Delay Factor': seasonal_factors[shipment_month]['delay'], # Added (for reference)
        'Proposed Freight Cost (USD)': proposed_freight_cost_usd,
        'Actual Freight Cost (USD)': actual_freight_cost_usd,
        'Cost Per Billable Kg (USD)': cost_per_billable_kg_usd,
        'Price Variance (USD)': price_variance_usd,
        'Price Variance (%)': price_variance_percent,
        'Carbon Emissions (kg CO2)': carbon_emissions_kg_co2, # Added
        'Status': status,
        'On-Time Delivery': on_time_delivery,
        'Cost Outlier': is_cost_outlier,
    })

df = pd.DataFrame(data)

# Ensure date columns are in datetime format and add temporal features
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Shipment Date'] = pd.to_datetime(df['Shipment Date'])
df['Actual Delivery Date'] = pd.to_datetime(df['Actual Delivery Date'])
df['Shipment Month'] = df['Shipment Date'].dt.month
df['Shipment Day of Week'] = df['Shipment Date'].dt.dayofweek

df.to_csv("../../data/raw/raw_logistics_data.csv",index=False )

columns_reqd = ['Order Date',
 'Shipment Date',
 'Actual Delivery Date',
 'Origin City',
 'Origin Country',
 'Destination Country',
 'Destination City',
 'Chosen Route Name',
 'Distance (km)',
 'Customer ID',
 'Service Level',
 'Product ID',
 'Product Category',
 'Shipment Content Type',
 'Line Item Quantity',
 'Unit Price (USD)',
 'Weight (kg)',
 'Volume (m³)',
 'Billable Weight (kg)',
 'Shipment Mode',
 'Transporter Name',
 'Carrier Product Fit Score',
 'Expected Delivery Time (Days)',
 'Avg Speed (km/h)',
 'Halt Duration (hours)',
 'Weather Impact',
 'Customs/Border Delay (hours)',
 'Proposed Freight Cost (USD)',
 'Actual Freight Cost (USD)',
 'Cost Per Billable Kg (USD)']

df[columns_df].to_csv("../../data/processed/processed_logistics_data.csv",index=False )

# Optional: Save to CSV
# df.to_csv('mock_logistics_data_full_enhanced.csv', index=False)
# print("\nData saved to mock_logistics_data_full_enhanced.csv")