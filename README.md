# dhis2py: A Python Package for DHIS2 API Interaction

`dhis2py` is a lightweight Python package designed to simplify interactions with DHIS2 APIs, enabling users to effortlessly pull various types of data for analysis and reporting.

## Features

- **Easy Authentication:** Connect to your DHIS2 instance securely.
- **Data Element Fetching:** Retrieve comprehensive information about data elements.
- **Category Option Combo Fetching:** Access details about category option combinations.
- **Organization Unit Fetching:** Pull data related to organizational units.
- **Dataset Fetching:** Efficiently retrieve data from specific datasets based on periods and organization units.
- **Data Resolution:** Resolve dataset values from IDs to human-readable names using provided mappings.

## Installation

You can install `dhis2py` using pip:

```bash
pip install git+https://github.com/deadex-ng/dhis2py.git
```

## Usage

Here's a quick guide on how to use dhis2py to pull data from your DHIS2 instance:

First, import the client module from dhis2py:
```python
from dhis2py import client
```

### 1. Initialize the DHIS2 Client

Set up your DHIS2 instance's base URL, username, and password, then create a DHIS2Client instance:
```python
base_url = "https://dhis2.health.gov.mw/api"
username = "your_username" 
password = "your_password"

dhis2_client = client.DHIS2Client(base_url, username, password)
```

### 2. Fetching Metadata
You can fetch various metadata from your DHIS2 instance:

#### Fetch Data Elements
```python
data_elements_response = dhis2_client.fetch_data_elements()
# data_elements_response will be a list of dictionaries, e.g.,
# [
#   {"id": "cydQh2bF96b", "name": "ANC 1st visit"},
#   {"id": "jP123456789", "name": "Delivery - Institutional"},
#   ...
# ]
```

#### Fetch Category Option Combos
```python
category_option_combos_response = dhis2_client.fetch_category_option_combos()
# category_option_combos_response will be a list of dictionaries, e.g.,
# [
#   {"id": "OOeO30zLg5m", "name": "Default"},
#   {"id": "W2S2h1d4f9j", "name": "Male"},
#   ...
# ]
```

### 3. Fetching Dataset Values
You can fetch data for specific datasets, periods, and organization units.

```python
dataset_ids = ["B0UtGNECmZW"]
periods = ["202401"]
org_units = ["pciHYsH4glX"] 

few_datasets = dhis2_client.fetch_multiple_datasets(dataset_ids, periods, org_units)
# few_datasets will contain the raw dataset values, typically with IDs for data elements and category option combos.
```

### 4. Resolving Dataset Values
To get human-readable names for data elements and category option combos in your fetched dataset values, use the resolve_dataset_values method with the maps you created earlier:

```python
resolved_data = dhis2_client.resolve_dataset_values(few_datasets, data_element_map, category_option_combo_map)

print(resolved_data)

# Example output of resolved_data (actual structure may vary slightly based on DHIS2 API response):
# [
#   {
#     "dataElement": "ANC 1st visit",
#     "categoryOptionCombo": "Default",
#     "orgUnit": "pciHYsH4glX", # orgUnit ID remains as is in this example, as it's not mapped in the example.
#     "period": "202401",
#     "value": "120"
#   },
#   {
#     "dataElement": "Delivery - Institutional",
#     "categoryOptionCombo": "Male",
#     "orgUnit": "pciHYsH4glX",
#     "period": "202401",
#     "value": "50"
#   }
# ]
```
The resolved_data will now contain the dataset values with data element and category option combo IDs replaced by their corresponding names, making the output much easier to understand.

## Contributing
We welcome contributions to `dhis2py`! Please feel free to open issues or submit pull requests.