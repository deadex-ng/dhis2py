import requests
from requests.auth import HTTPBasicAuth

class DHIS2Client:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

        self.data_elements_by_id = {}
        self.data_elements_by_name = {}
        self.coc_by_id = {}
        self.coc_by_name = {}
        self.org_units_by_id = {}
        self.org_units_by_name = {}
        self.session.auth = HTTPBasicAuth(username.strip(), password.strip())
        self.session.headers.update({"Accept": "application/json"})

    def get(self, endpoint: str, params=None):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=120, verify=True)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                raise ValueError("Unauthorized: Check your DHIS2 username/password.") from http_err
            elif 500 <= response.status_code < 600:
                raise ConnectionError("Server error: DHIS2 might be down or overloaded.") from http_err
            raise http_err
        except requests.exceptions.Timeout as timeout_err:
            raise TimeoutError(f"Request to {url} timed out.") from timeout_err
        except requests.exceptions.ConnectionError as conn_err:
            raise ConnectionError(f"Failed to connect to {url}.") from conn_err

    def fetch_data_elements(self):
        try:
            response = self.get("dataElements", params={"paging": "false", "fields": "id,name"})
            elements = response.get("dataElements", [])
            self.data_elements_by_id = {el["id"]: el["name"] for el in elements}
            self.data_elements_by_name = {el["name"]: el["id"] for el in elements}
            return elements
        except Exception as e:
            raise RuntimeError(f"Failed to fetch data elements: {e}") from e

    def get_data_element_name(self, element_id):
        if not self.data_elements_by_id:
            self.fetch_data_elements()
        return self.data_elements_by_id.get(element_id)

    def get_data_element_id(self, element_name):
        if not self.data_elements_by_name:
            self.fetch_data_elements()
        return self.data_elements_by_name.get(element_name)

    def fetch_category_option_combos(self):
        try:
            response = self.get("categoryOptionCombos", params={"paging": "false", "fields": "id,name"})
            cat_option_combos = response.get("categoryOptionCombos", [])
            self.coc_by_id = {coc["id"]: coc["name"] for coc in cat_option_combos}
            self.coc_by_name = {coc["name"]: coc["id"] for coc in cat_option_combos}
            return cat_option_combos
        except Exception as e:
            raise RuntimeError(f"Failed to fetch category option combos: {e}") from e

    def get_category_option_combo_name(self, coc_id):
        if not self.coc_by_id:
            self.fetch_category_option_combos()
        return self.coc_by_id.get(coc_id)

    def get_category_option_combo_id(self, coc_name):
        if not self.coc_by_name:
            self.fetch_category_option_combos()
        return self.coc_by_name.get(coc_name)

    def fetch_dataset(self, dataset_id: str, period: str, org_unit: str = None):
        params = {"dataSet": dataset_id, "period": period}
        if org_unit:
            params["orgUnit"] = org_unit

        try:
            return self.get("dataValueSets", params=params)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch dataset {dataset_id} for period {period}: {e}") from e

    def fetch_datasets(self):
        try:
            response = self.get("dataSets", params={"paging": "false", "fields": "id,name"})
            return response.get("dataSets", [])
        except Exception as e:
            raise RuntimeError(f"Failed to fetch datasets: {e}") from e

    def fetch_multiple_datasets(self, dataset_ids: list, periods: list, org_units: list):
        all_data = []

        for dataset_id in dataset_ids:
            for period in periods:
                for org_unit in org_units:
                    try:
                        result = self.fetch_dataset(dataset_id, period, org_unit)
                        all_data.append({
                            "dataset_id": dataset_id,
                            "period": period,
                            "orgUnit": org_unit,
                            "data": result
                        })
                    except Exception as e:
                        # Continue fetching others even if one fails
                        all_data.append({
                            "dataset_id": dataset_id,
                            "period": period,
                            "orgUnit": org_unit,
                            "error": str(e)
                        })
        return all_data

    def fetch_org_units(self):
        try:
            response = self.get("organisationUnits", params={"paging": "false", "fields": "id,name"})
            org_units = response.get("organisationUnits", [])
            self.org_units_by_id = {ou["id"]: ou["name"] for ou in org_units}
            self.org_units_by_name = {ou["name"]: ou["id"] for ou in org_units}
            return org_units
        except Exception as e:
            raise RuntimeError(f"Failed to fetch organisation units: {e}") from e

    def resolve_dataset_values(self, few_datasets, data_element_map, category_option_combo_map):
        resolved_list = []
        for dataset in few_datasets:
            # print(dataset.get('data').get('dataValues'))
            for el in dataset.get('data').get('dataValues'):
                # print(el)
                for ele in el:
                    eid = el.get('dataElement')
                    catoid = el.get('categoryOptionCombo')
                    period = el.get('period')
                    org_unitid = el.get('orgUnit')
                    value = el.get('value')
                    neid = self.data_elements_by_id.get(eid)
                    ncatoid = self.coc_by_id.get(catoid)
                    norg_unit = self.org_units_by_id.get(org_unitid)
                    # print(eid,":", neid, ":", ncatoid)
                    cc = {
                        'data element': neid,
                        'category option combination': ncatoid,
                        'period': period,
                        'org unit' : norg_unit,
                        'value' : value
                    }
                    resolved_list.append(cc)
        return resolved_list
