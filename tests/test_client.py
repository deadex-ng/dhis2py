import unittest
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError, Timeout, ConnectionError
from dhis2py.client import DHIS2Client

class TestDHIS2Client(unittest.TestCase):
    def setUp(self):
        self.base_url = "https://play.im.dhis2.org/stable-2-42-1/api/"
        self.username = "admin"
        self.password = "district"
        self.client = DHIS2Client(self.base_url, self.username, self.password)

    @patch('dhis2py.client.requests.Session.get')
    def test_fetch_data_elements_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "dataElements": [
                {"id": "abc123", "name": "Test Element A"},
                {"id": "def456", "name": "Test Element B"}
            ]
        }

        mock_get.return_value = mock_response
        
        elements = self.client.fetch_data_elements()
        self.assertEqual(len(elements), 2)
        self.assertIn("abc123", self.client.data_elements_by_id)
        self.assertEqual(self.client.get_data_element_name("abc123"), "Test Element A")
        self.assertEqual(self.client.get_data_element_id("Test Element B"), "def456")

    @patch('dhis2py.client.requests.Session.get')
    def test_fetch_data_elements_empty(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"dataElements": []}
        mock_get.return_value = mock_response

        elements = self.client.fetch_data_elements()

        self.assertEqual(elements, [])
        self.assertEqual(self.client.data_elements_by_id, {})
        self.assertIsNone(self.client.get_data_element_name("nonexistent"))

    @patch('dhis2py.client.requests.Session.get')
    def test_http_error_401(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = HTTPError("401 Unauthorized")
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with self.assertRaises(RuntimeError) as context:
            self.client.fetch_data_elements()
        self.assertIn("401 Unauthorized", str(context.exception))

    @patch('dhis2py.client.requests.Session.get')
    def test_http_error_500(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = HTTPError("500 Server Error")
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with self.assertRaises(RuntimeError) as context:
            self.client.fetch_data_elements()
        self.assertIn("Server error", str(context.exception))

    @patch('dhis2py.client.requests.Session.get')
    def test_http_error_unknown(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = HTTPError("403 Forbidden")
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        with self.assertRaises(RuntimeError):
            self.client.fetch_data_elements()

    @patch('dhis2py.client.requests.Session.get')
    def test_timeout_error(self, mock_get):
        mock_get.side_effect = Timeout("Request timed out")

        with self.assertRaises(RuntimeError) as context:
            self.client.fetch_data_elements()
        self.assertIn("timed out", str(context.exception))

    @patch('dhis2py.client.requests.Session.get')
    def test_connection_error(self, mock_get):
        mock_get.side_effect = ConnectionError("Failed to connect")

        with self.assertRaises(RuntimeError) as context:
            self.client.fetch_data_elements()
        self.assertIn("Failed to connect", str(context.exception))

    # --------------------------
    # Category Option Combo Tests
    # --------------------------

    @patch('dhis2py.client.requests.Session.get')
    def test_fetch_category_option_combos_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "categoryOptionCombos": [
                {"id": "coc123", "name": "Option A"},
                {"id": "coc456", "name": "Option B"}
            ]
        }
        mock_get.return_value = mock_response

        combos = self.client.fetch_category_option_combos()

        self.assertEqual(len(combos), 2)
        self.assertEqual(self.client.get_category_option_combo_name("coc123"), "Option A")
        self.assertEqual(self.client.get_category_option_combo_id("Option B"), "coc456")

    @patch('dhis2py.client.requests.Session.get')
    def test_fetch_category_option_combos_empty(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"categoryOptionCombos": []}
        mock_get.return_value = mock_response

        combos = self.client.fetch_category_option_combos()

        self.assertEqual(combos, [])
        self.assertEqual(self.client.coc_by_id, {})
        self.assertIsNone(self.client.get_category_option_combo_name("nonexistent"))

    @patch('dhis2py.client.requests.Session.get')
    def test_fetch_category_option_combos_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_get.return_value = mock_response

        with self.assertRaises(RuntimeError) as context:
            self.client.fetch_category_option_combos()
        self.assertIn("HTTP Error", str(context.exception))

    # --------------------------
    # Datasets Tests
    # --------------------------

    @patch('dhis2py.client.requests.Session.get')
    def test_fetch_dataset_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "dataValues": [{"dataElement": "abc123", "value": "10"}]
        }
        mock_get.return_value = mock_response

        result = self.client.fetch_dataset("dataset123", "202401", "orgUnit123")

        self.assertIn("dataValues", result)
        self.assertEqual(result["dataValues"][0]["dataElement"], "abc123")

    @patch('dhis2py.client.requests.Session.get')
    def test_fetch_dataset_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Fetch failed")
        mock_get.return_value = mock_response

        with self.assertRaises(RuntimeError) as context:
            self.client.fetch_dataset("dataset123", "202401", "orgUnit123")
        self.assertIn("Failed to fetch dataset", str(context.exception))

    @patch('dhis2py.client.requests.Session.get')
    def test_fetch_datasets_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "dataSets": [
                {"id": "ds1", "name": "Dataset A"},
                {"id": "ds2", "name": "Dataset B"}
            ]
        }
        mock_get.return_value = mock_response

        datasets = self.client.fetch_datasets()
        self.assertEqual(len(datasets), 2)
        self.assertEqual(datasets[0]["id"], "ds1")

    @patch('dhis2py.client.requests.Session.get')
    def test_fetch_multiple_datasets_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"dataValues": []}
        mock_get.return_value = mock_response

        results = self.client.fetch_multiple_datasets(
            dataset_ids=["ds1", "ds2"],
            periods=["202401", "202402"],
            org_units=["ou1"]
        )
        
        self.assertEqual(len(results), 4)  # 2 datasets * 2 periods * 1 org unit
        for result in results:
            self.assertIn("dataset_id", result)
            self.assertIn("period", result)
            self.assertIn("orgUnit", result)
            self.assertIn("data", result)

    @patch('dhis2py.client.requests.Session.get')
    def test_fetch_multiple_datasets_partial_failure(self, mock_get):
        def side_effect(*args, **kwargs):
            if "ds2" in kwargs["params"]["dataSet"]:
                raise Exception("Simulated failure")
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = {"dataValues": []}
            return mock_response

        mock_get.side_effect = side_effect

        results = self.client.fetch_multiple_datasets(
            dataset_ids=["ds1", "ds2"],
            periods=["202401"],
            org_units=["ou1"]
        )

        self.assertEqual(len(results), 2)
        success = [r for r in results if "data" in r]
        failure = [r for r in results if "error" in r]

        self.assertEqual(len(success), 1)
        self.assertEqual(len(failure), 1)
        self.assertIn("Simulated failure", failure[0]["error"])

if __name__ == '__main__':
    unittest.main()
