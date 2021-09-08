import json
import fitbit
import unittest
import requests

api = fitbit.API(debug=True)

class FitbitTestMethods(unittest.TestCase):

    def tearDown(self) -> None:
        print(json.loads(self.res.text))
        self.assertTrue(self.res.status_code == requests.codes.ok)

    """Activity"""
    def test_activity_summary(self):
        self.res = api.activity_summary("2021-08-11")

    # def test_log_activity(self):
    #     pass

    def test_lifetime_stats(self):
        self.res = api.lifetime_stats()

    # def test_delete_activity_log(self):
    #     pass

    # def test_activity_log_list(self):
    #     pass

    # def test_activity_tcx(self):
    #     pass

    # def test_activity_types(self):
    #     pass

    # def test_activity_type(self):
    #     pass

    # def test_frequent_activities(self):
    #     pass

    # def test_recent_activity_types(self):
    #     pass

    # def test_favorite_activities(self):
    #     pass

    # def test_delete_favorite_activity(self):
    #     pass

    # def test_add_favorite_activity(self):
    #     pass

    # def test_activity_goals(self):
    #     pass

    # def test_update_activity_goals(self):
    #     pass

    # """Activity Intraday Time Series"""
    # def test_activity_intraday(self):
    #     pass

if __name__ == "__main__":
    unittest.main()