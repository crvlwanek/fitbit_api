import json
import fitbit
import unittest
import requests

api = fitbit.API(debug=True)

def log(res):
    print(json.dumps(json.loads(res.text), indent=1))

class FitbitTestMethods(unittest.TestCase):

    def tearDown(self) -> None:
        # log(self.res)
        self.assertTrue(self.res.status_code == requests.codes.ok)

    """Activity"""
    def test_activity_types(self):
        self.res = api.activity_types()

    def test_activity_type(self):
        self.res = api.activity_type(17105)

    def test_lifetime_stats(self):
        self.res = api.lifetime_stats()

    def test_activity_summary(self):
        self.res = api.activity_summary("2021-08-11")

    def test_activity_log_list(self):
        self.res = api.activity_log_list("2021-09-08", "before", "desc", 1)

    def test_log_activity(self):
        self.res = api.log_activity(17105, "id", 200, "11:30:01", 40000, "2021-09-08", 3.00)
        self.log_id = json.loads(self.res.text)["activityLog"]["logId"]

    def test_delete_activity_log(self):
        self.res = api.delete_activity_log(self.log_id)

    def test_activity_tcx(self):
        self.res = api.activity_tcx(42686450461)

    def test_frequent_activities(self):
        self.res = api.frequent_activities()

    def test_recent_activity_types(self):
        self.res = api.recent_activity_types()

    def test_favorite_activities(self):
        self.res = api.favorite_activities()

    def test_add_favorite_activity(self):
        self.res = api.add_favorite_activity(90009)

    def test_delete_favorite_activity(self):
        self.res = api.delete_favorite_activity(90009)

    def test_activity_goals(self):
        self.res = api.activity_goals("daily")

    def test_update_activity_goals(self):
        self.res = api.update_activity_goals("daily", "floors", "20")

    """Activity Intraday Time Series"""
    def test_activity_intraday(self):
        self.res = api.activity_intraday("steps", "2021-09-06", "1d", "1min")
    
    """Activity Time Series"""
    def test_activity_time_series(self):
        self.res = api.activity_time_series("calories", "2021-09-01", "7d")

    """Auth"""
    def test_access_token(self):
        token = api.access_token
        self.res = api.get_access_token("refresh")
        self.assertNotEqual(token, api.access_token)

    """Body and Weight"""
    def test_body_weight_logs(self):
        self.res = api.body_logs("weight", "2021-09-08")

    def test_body_fat_logs(self):
        self.res = api.body_logs("fat", "2021-09-01", "7d")

    def test_log_body_weight(self):
        self.res = api.log_body("weight", 170.00, "2017-09-08", "12:30:01")
        self.body_weight_log_id = self.res.json()["weightLog"]["logId"]

    def test_log_body_fat(self):
        self.res = api.log_body("fat", 20.5, "2017-09-08", "12:30:01")
        self.body_fat_log_id = self.res.json()["fatLog"]["logId"]

    def test_delete_body_weight_log(self):
        self.res = api.delete_body_log("weight", self.body_weight_log_id)

    def test_delete_body_fat_log(self):
        self.res = api.delete_body_log("fat", self.body_fat_log_id)

    def test_body_goals(self):
        self.res = api.body_goals("weight")

    def test_update_body_fat_goal(self):
        self.res = api.update_body_fat_goal(16.00)

    def test_update_body_weight_goal(self):
        self.res = api.update_body_weight_goal("2017-01-01", 210.0, 160.0)

    """Body and Weight Time Series"""
    def test_body_time_series(self):
        self.res = api.body_time_series("bmi", "2021-09-01", "1m")

    """Devices"""
    def test_devices(self):
        self.res = api.devices()
        self.tracker_id = self.res.json()[0]['id']

    def test_alarms(self):
        self.res = api.alarms(self.tracker_id)

    def test_add_alarm(self):
        self.res = api.add_alarm(self.tracker_id, "11:30-05:00", False, False, "MONDAY")
        self.alarm_id = self.res.json()["trackerAlarm"]["alarmId"]

    def test_update_alarm(self):
        self.res = api.update_alarm(self.tracker_id, self.alarm_id, "11:00-05:00", False, False, "TUESDAY", 15, 15)

    def test_delete_alarm(self):
        api.delete_alarm(self.tracker_id, self.alarm_id)

    """Food and Water"""
    def test_food_locales(self):
        pass

    def test_food_goals(self):
        pass

    def test_update_food_goal(self):
        pass

    def test_food_logs(self):
        pass

    def test_water_logs(self):
        pass

    def test_water_goal(self):
        pass

    def test_update_water_goal(self):
        pass

    def test_log_food(self):
        pass

    def test_delete_food_log(self):
        pass

    def test_edit_food_log(self):
        pass

    def test_log_water(self):
        pass

    def test_delete_water_log(self):
        pass

    def test_update_water_log(self):
        pass

    def test_favorite_foods(self):
        pass

    def test_frequent_foods(self):
        pass

    def test_add_favorite_foods(self):
        pass

    def test_delete_favorite_food(self):
        pass

    def test_meals(self):
        pass

    def test_create_meal(self):
        pass

    def test_edit_meal(self):
        pass

    def test_delete_meal(self):
        pass

    def test_recent_foods(self):
        pass

    def test_create_food(self):
        pass

    def test_delete_custom_food(self):
        pass

    def test_food(self):
        pass

    def test_food_units(self):
        pass

    def test_search_foods(self):
        pass

    """Food and Water Time Series"""
    def test_food_or_water_time_series(self):
        pass

    """Friends"""
    def test_friends(self):
        pass

    def test_friends_leaderboard(self):
        pass

    def test_friend_invitations(self):
        pass

    def test_invite_friends(self):
        pass

    def test_friend_invitation(self):
        pass

    """Heart Rate Intraday Time Series"""
    def test_heart_rate_intraday(self):
        pass

    """Heart Rate Time Series"""
    def test_heart_rate_time_series(self):
        pass

    """Sleep"""
    def test_delete_sleep_log(self):
        pass

    def test_sleep_log(self):
        pass

    def test_sleep_logs_range(self):
        pass

    def test_sleep_logs_list(self):
        pass

    def test_sleep_goal(self):
        pass

    def test_update_sleep_goal(self):
        pass

    def test_log_sleep(self):
        pass

    """Subscriptions"""
    def test_subscriptions(self):
        pass

    def test_add_subscription(self):
        pass

    def test_delete_subscription(self):
        pass

    """User"""
    def test_badges(self):
        pass

    def test_profile(self):
        pass

    def test_update_profile(self):
        pass

if __name__ == "__main__":
    unittest.main()