import requests, pyperclip, base64, os, json
from typing import Union

class Fitbit:

  auth_url = "https://www.fitbit.com/oauth2/authorize"

  redirect_uri = "http://localhost"
  
  client_id = os.environ.get("fitbit_client_id")
  client_secret = os.environ.get("fitbit_client_secret")
  
  scope = ["activity", "nutrition", "heartrate", "location", "nutrition", "profile", "settings", "sleep", "social", "weight"]

class API:

  token_url = "https://api.fitbit.com/oauth2/token"
  base_url = "https://api.fitbit.com"
  
  @staticmethod
  def copy_auth_url() -> None:
    """Copies the authorization url to the user's clipboard"""
    req = requests.Request("GET", Fitbit.auth_url, params={
      "response_type": "code", "client_id": Fitbit.client_id, 
      "redirect_uri": Fitbit.redirect_uri, "scope": " ".join(Fitbit.scope)
    }).prepare()
    pyperclip.copy(req.url)
    print(f"Visit the following url to get your auth code: {req.url}")
      
  @staticmethod
  def encoded_client() -> str:
    """Returns the base64 encoding of the user's client_id and client_secret"""
    return base64.b64encode(f"{Fitbit.client_id}:{Fitbit.client_secret}".encode('ascii')).decode('ascii') 
          
  def __init__(self, *, debug=False):
    self.debug = debug
    self.client = API.encoded_client()
    self.get_access_token("auth")

  def __set_user_and_tokens(self, res) -> None:
    assert res.status_code == 200
    data = res.json()
    self.user_id = data["user_id"]
    self.access_token = data["access_token"]
    self.refresh_token = data["refresh_token"]
      
  def authenticate(self, auth_code: str) -> dict:
    """
    Uses an auth_code to authenticate the user and stores instance info in
    self.user_id, self.access_token, and self.refresh_token
    """
    res = requests.post(API.token_url, 
      params={
        "code": auth_code, "grant_type": "authorization_code", 
        "client_id": Fitbit.client_id, "redirect_uri": Fitbit.redirect_uri}, 
      headers={
        "Authorization": f"Basic {self.client}", 
        "Content-Type": "application/x-www-form-urlencoded"})
    self.__set_user_and_tokens(res)
    if self.debug:
      return res
    return res.json()

  def refresh(self) -> dict:
    """Uses a refresh_token and sets instance info with a new access_token and refresh_token"""
    res = requests.post(API.token_url,
      params={
        "grant_type": "refresh_token", "refresh_token": self.refresh_token},
      headers={
        "Authorization": f"Basic {self.client}", 
        "Content-Type": "application/x-www-form-urlencoded"})
    self.__set_user_and_tokens(res)
    if self.debug:
      return res
    return res.json()
      
  def __request(self, http_method, url: str, *, params: dict = {}, headers: dict = {}, data: dict = {}, is_json: bool = True) -> dict:
    """
    Sends a request to the API base url using the specified method

    Parameters:
      http_method: requests.get, requests.post, requests.delete
      url: The location of the API endpoint
      params: (optional) A dictionary of query parameters
      headers: (optional) A dictionary of header parameters
      data: (optional) A dictionary of form data (payload) parameters
      is_json: (optional) Whether the response is json data or not
    """
    headers = { "Authorization": f"Bearer {self.access_token}" }
    res = http_method(f"{API.base_url}{url}",headers=headers,params=params,data=data)
    if self.debug: 
      return res
    if is_json:
      return res.json()
    return res.text
  
  def __get(self, url: str, *, params: dict = {}, headers: dict = {}, data: dict = {}, is_json: bool = True) -> dict:
    """
    Sends a GET request to the API base url

    Parameters:
      url: The location of the API endpoint
      params: (optional) A dictionary of query parameters
      headers: (optional) A dictionary of header parameters
      data: (optional) A dictionary of form data (payload) parameters
      is_json: (optional) Whether the response is json data or not
    """
    return self.__request(requests.get, url, params=params, headers=headers, data=data, is_json=is_json)
  
  def __post(self, url: str, *, params: dict = {}, headers: dict = {}, data: dict = {}, is_json: bool = True) -> dict:
    """
    Sends a POST request to the API base url

    Parameters:
      url: The location of the API endpoint
      params: (optional) A dictionary of query parameters
      headers: (optional) A dictionary of header parameters
      data: (optional) A dictionary of form data (payload) parameters
      is_json: (optional) Whether the response is json data or not
    """
    return self.__request(requests.post, url, params=params, headers=headers, data=data, is_json=is_json)
  
  def __delete(self, url: str, *, params: dict = {}, headers: dict = {}, data: dict = {}, is_json: bool = True) -> dict:
    """
    Sends a DELETE request to the API base url

    Parameters:
      url: The location of the API endpoint
      params: (optional) A dictionary of query parameters
      headers: (optional) A dictionary of header parameters
      data: (optional) A dictionary of form data (payload) parameters
      is_json: (optional) Whether the response is json data or not
    """
    return self.__request(requests.delete, url, params=params, headers=headers, data=data, is_json=is_json)

  """
  Activity
  
  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/activity/
  """
  def activity_types(self) -> dict:
    """
    Retreives a tree of all valid Fitbit public activities from the activities catelog as well as 
    private custom activities the user created in the format requested.
    """
    return self.__get(f"/1/activities.json")

  def activity_type(self, activity_id: int) -> dict:
    """
    Returns the detail of a specific activity in the Fitbit activities database in the format 
    requested. If activity has levels, it also returns a list of activity level details.
    
    Parameters:
      activity_id: The activity ID.
    """
    return self.__get(f"/1/activities/{activity_id}.json")
    
  def lifetime_stats(self) -> dict:
    """
    Updates a user's daily activity goals and returns a response using units in the 
    unit system which corresponds to the Accept-Language header provided.
    """
    return self.__get(f"/1/user/{self.user_id}/activities.json")

  def activity_summary(self, date: str) -> dict:
    """
    Retrieves a summary and list of a user's activities and activity log entries for a given day.

    Parameters:
      date: The date in the format yyyy-MM-dd
    """
    return self.__get(f"/1/user/{self.user_id}/activities/date/{date}.json")
  
  def activity_log_list(self, date: str, date_type: str, sort: str, limit: int, offset: int = 0) -> dict:
    """
    Retreives a list of user's activity log entries before or after a given day with offset and limit using 
    units in the unit system which corresponds to the Accept-Language header provided.

    Parameters:
      date: The date in the format yyyy-MM-ddTHH:mm:ss. Only yyyy-MM-dd is required. Either beforeDate or afterDate should be specified.
      date_type: before or after
      sort: The sort order of entries by date asc (ascending) or desc (descending).
      limit: The maximum number of entries returned (maximum 100).
      offset: The offset number of entries.
    """
    return self.__get(f"/1/user/{self.user_id}/activities/list.json", 
      params={f"{date_type}Date": date, "sort": sort, "offset": offset, "limit": limit})

  def log_activity(self, activity_id: Union[str, int], id_type: str, manual_calories: int, start_time: str, duration_millis: int, date: str, distance: float) -> dict:
    """
    The Log Activity endpoint creates log entry for an activity or user's private custom activity 
    using units in the unit system which corresponds to the Accept-Language header provided 
    and get a response in the format requested.

    Parameters:
      activity_id: The ID or custom name of the activity, directory activity or intensity level activity.
      id_type: id or name
      manual_calories: Calories burned that are manaully specified.
      start_time: Activity start time. Hours and minutes in the format HH:mm:ss.
      duration_millis: Duration in milliseconds.
      date: Log entry date in the format yyyy-MM-dd.
      distance: Distance is required for logging directory activity in the format X.XX and in the selected distanceUnit.
    """
    return self.__post(f"/1/user/{self.user_id}/activities.json", 
      params={f"activity{id_type.capitalize()}": activity_id, "manualCalories": manual_calories,
      "startTime": start_time, "durationMillis": duration_millis, "date": date, "distance": distance})
  
  def delete_activity_log(self, activity_log_id: int) -> dict:
    """
    Deletes a user's activity log entry with the given ID.

    Parameters:
      activity_log_id: The id of the activity log entry.
    """
    return self.__delete(f"/1/user/{self.user_id}/activities/{activity_log_id}.json")
  
  def activity_tcx(self, log_id: int, include_partial_tcx: bool = True) -> str:
    """
    Retreives the details of a user's location and heart rate data during a logged exercise activity.

    Parameters:
      log_id: The activity's log ID.
      include_partial_tcx: Include TCX points regardless of GPS data being present.
    """
    return self.__get(f"/1/user/{self.user_id}/activities/{log_id}.tcx",
      params={"includePartialTCX": include_partial_tcx}, is_json=False)
  
  def frequent_activities(self) -> dict:
    """
    Retreives a list of a user's frequent activities in the format requested using units 
    in the unit system which corresponds to the Accept-Language header provided.
    """
    return self.__get(f"/1/user/{self.user_id}/activities/frequent.json")
  
  def recent_activity_types(self) -> dict:
    """
    Retreives a list of a user's recent activities types logged with some details of the last activity 
    log of that type using units in the unit system which corresponds to the Accept-Language header provided.
    """
    return self.__get(f"/1/user/{self.user_id}/activities/recent.json")
  
  def favorite_activities(self) -> dict:
    """Returns a list of a user's favorite activities."""
    return self.__get(f"/1/user/{self.user_id}/activities/favorite.json")
  
  def add_favorite_activity(self, activity_id: int) -> None:
    """
    Adds the activity with the given ID to user's list of favorite activities.

    Parameters:
      activity_id: The encoded ID of the activity.
    """
    return self.__post(f"/1/user/{self.user_id}/activities/favorite/{activity_id}.json")

  def delete_favorite_activity(self, activity_id: int) -> None:
    """
    Removes the activity with the given ID from a user's list of favorite activities.

    Parameters:
      activity_id: The ID of the activity to be removed.
    """
    return self.__delete(f"/1/user/{self.user_id}/activities/favorite/{activity_id}.json", is_json=False)
  
  def activity_goals(self, period: str):
      """
      Retreives a user's current daily or weekly activity goals using measurement units as defined in the 
      unit system, which corresponds to the Accept-Language header provided.

      Parameters:
        period: daily or weekly
      """
      return self.__get(f"/1/user/{self.user_id}/activities/goals/{period}.json")
  
  def update_activity_goals(self, period: str, type: str, value: str) -> dict:
    """
    Updates a user's daily or weekly activity goals and returns a response using units in the unit system 
    which corresponds to the Accept-Language header provided.

    Parameters:
      period: daily or weekly
      type: activeMinutes, caloriesOut, distance, floors, or steps for daily; distance, floors, or steps for weekly
      value: goal value
    """
    return self.__post(f"/1/user/{self.user_id}/activities/goals/{period}.json",
      params={"type": type, "value": value})
  
  """
  Activity Intraday Time Series
  
  Full documentation:
    https://dev.fitbit.com/build/reference/web-api/activity/#get-activity-intraday-time-series
  """
  def activity_intraday(self, resource_path: str, base_date: str, end_or_1d: str, detail_level: str, start_time: str = None, end_time: str = None) -> dict:
    """
    Returns the Activity Intraday Time Series for a given resource in the format requested.

    Parameters:
      resource_path: calories, steps, distance, floors, or elevation
      base_date: The range start date in the format yyyy-MM-dd or today.
      end_or_1d: Either an end date in the format yyyy-MM-dd or the string "1d" for a single day of data
      detail_level: Number of data points to include. Either 1min or 15min
      start_time: (optional) The start of the period in the format HH:mm.
      end_time: (optional) The end of the period in the format HH:mm
    """
    if start_time is not None and end_time is not None:
      time = f"/time/{start_time}/{end_time}"
    else:
      time = ""
    return self.__get(f"/1/user/{self.user_id}/activities/{resource_path}/date/{base_date}/{end_or_1d}/{detail_level}{time}.json")

  """
  Activity Time Series
  
  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/activity/#activity-time-series
  """
  
  def activity_time_series(self, resource_path: str, base_date: str, end_or_period: str, use_tracker: bool = False):
    """
    Returns activities time series data in the specified range for a given resource.

    Parameters:
      resource_path: calories, caloriesBMR, steps, distance, floors, elevation, minutesSedentary, minutesLightlyActive, minutesFairlyActive, minutesVeryActive, or activityCalories
      base_date: If an end date is provided, base_date refers to the start date. If a period is provided instead, base_date will be the last date of that period. Format yyyy-MM-dd
      end_or_period: A date in the format yyyy-MM-dd or one of the following periods: 1d, 7d, 30d, 1w, 1m, 3m, 6m, 1y, or max
      use_tracker: (optional) If true, only tracker data is returned
    """
    tracker = "tracker/" if use_tracker else ""
    return self.__get(f"/1/user/{self.user_id}/activities/{tracker}/{resource_path}/date/{base_date}/{end_or_period}.json")
  
  """
  Auth
  
  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/oauth2/
  """
  def get_access_token(self, type: str) -> str:
    """
    Authenticates the user and stores the user_id, access_token, and refresh_token in the fitbit.API instance. Use
    a type of "auth" to authenticate a user, and a type of "refresh" to use an existing refresh token

    Parameters:
      type: auth or refresh
    """
    if type == "auth":
      API.copy_auth_url()
      self.authenticate(input("Auth code: "))
    else:
      self.refresh()
    return self.access_token
  
  """
  Body and Weight
  
  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/body/
  """
  def body_logs(self, resource_path: str, base_date: str, end_or_period: Union[str, None] = None):
    """
    Retreives a list of all user's weight or body fat log entries for a given day in the format requested.

    Parameters:
      resource_path: weight or fat
      base_date: If an end date is provided, base_date refers to the start date. If a period is provided instead, base_date will be the last date of that period. If neither is provided, a single log for the day specified is returned. Format yyyy-MM-dd
      end_or_period: (optional) A date in the format yyyy-MM-dd or one of the following periods: 1d, 7d, 30d, 1w, 1m, 3m, 6m, 1y, or max
    """
    if end_or_period is not None:
      end = f"/{end_or_period}"
    else:
      end = ""
    return self.__get(f"/1/user/{self.user_id}/body/log/{resource_path}/date/{base_date}{end}.json")
  
  def log_body(self, resource_path: str, measurement: float, date: str, time: str):
    """
    Creates a log entry for weight or body fat and returns a response in the format requested

    Parameters:
      resource_path: weight or fat
      measurement: the measurement to record
      date: Log entry date in the format yyyy-MM-dd.
      time: Log entry time in the format HH:mm:ss.
    """
    return self.__post(f"/1/user/{self.user_id}/body/log/{resource_path}.json",
      params={resource_path: measurement, "date": date, "time": time})
  
  def delete_body_log(self, resource_path: str, body_log_id: int):
    """
    Deletes a user's weight or body fat log entry with the given ID.

    Parameters:
      resource_path: weight or fat
      body_log_id: The id of the weight or body fat log entry
    """
    return self.__delete(f"/1/user/{self.user_id}/body/log/{resource_path}/{body_log_id}.json")
  
  def body_goals(self, goal_type: str):
    """
    Retreives a user's current body fat percentage or weight goal using units in the unit systems that 
    corresponds to the Accept-Language header providedin the format requested.

    Parameters:
      goal_type: weight or fat
    """
    return self.__get(f"/1/user/{self.user_id}/body/log/{goal_type}/goal.json")
  
  def update_body_fat_goal(self, fat: float):
    """
    Updates user's fat percentage goal.

    Parameters:
      fat: Target body fat percentage; in the format X.XX
    """
    return self.__post(f"/1/user/{self.user_id}/body/log/fat/goal.json",
      params={"fat": fat})

  def update_body_weight_goal(self, start_date: str, start_weight: float, weight: float):
    """
    Updates user's fat percentage goal.

    Parameters:
      start_date: Weight goal start date; in the format yyyy-MM-dd.
      start_weight: Weight goal start weight; in the format X.XX, in the unit systems that corresponds to the Accept-Language header provided.
      weight: Weight goal target weight; in the format X.XX, in the unit systems that corresponds to the Accept-Language header provided; required if user doesn't have an existing weight goal.
    """
    return self.__post(f"/1/user/{self.user_id}/body/log/weight/goal.json",
      params={"startDate": start_date, "startWeight": start_weight, "weight": weight})
  
  """
  Body and Weight Time Series
  
  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/body/#body-time-series
  """
  def body_time_series(self, resource_path: str, base_date: str, end_or_period: str):
      """
      Returns time series data in the specified range for a given resource in the format requested using units in the 
      unit system that corresponds to the Accept-Language header provided.

      Parameters:
        resource_path: bmi, fat, or weight
        base_date: If an end date is provided, base_date refers to the start date. If a period is provided instead, base_date will be the last date of that period.
        end_or_period: (optional) A date in the format yyyy-MM-dd or one of the following periods: 1d, 7d, 30d, 1w, 1m, 3m, 6m, 1y, or max
      """
      return self.__get(f"/1/user/{self.user_id}/body/{resource_path}/date/{base_date}/{end_or_period}.json")
  
  """
  Devices
  
  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/devices/
  """
  def devices(self):
      """Returns a list of the Fitbit devices connected to a user's account."""
      return self.__get(f"/1/user/{self.user_id}/devices.json")
  
  def alarms(self, tracker_id: int):
      """
      Returns alarms for a device

      Parameters:
        tracker_id: The ID of the tracker for which data is returned. The tracker-id value is found via the Get Devices endpoint.
      """
      return self.__get(f"/1/user/{self.user_id}/devices/tracker/{tracker_id}/alarms.json")
  
  def add_alarm(self, tracker_id: int, time: str, enabled: bool, recurring: bool, week_days: str):
      """
      Adds the alarm settings to a given ID for a given device.

      Parameters:
        tracker_id: The ID of the tracker for which data is returned. The tracker-id value is found via the Get Devices endpoint.
        time: Time of day that the alarm vibrates with a UTC timezone offset, e.g. 07:15-08:00.
        enabled: True or False. If False, alarm does not vibrate until enabled is set to True.
        recurring: True or False. If False, the alarm is a single event.
        week_days: Comma separated list of days of the week on which the alarm vibrates, e.g. MONDAY, TUESDAY.
      """
      return self.__post(f"/1/user/{self.user_id}/devices/tracker/{tracker_id}/alarms.json",
          params={"time": time, "enabled": enabled, "recurring": recurring, "weekDays": week_days})
  
  def update_alarm(self, tracker_id: int, alarm_id: int, time: str, enabled: bool, recurring: bool, week_days: str, snooze_length: int, snooze_count: int):
      """
      Updates the alarm entry with a given ID for a given device. It also gets a response in the format requested.

      Parameters:
        tracker_id: The ID of the tracker for which data is returned. The tracker-id value is found via the Get Devices endpoint.
        alarm_id: The ID of the alarm to be updated. The alarm-id value is found in the response of the Get Activity endpoint.
        time: Time of day that the alarm vibrates with a UTC timezone offset, e.g. 07:15-08:00.
        enabled: True or False. If False, alarm does not vibrate until enabled is set to True.
        recurring: true or false. If false, the alarm is a single event.
        week_days: Comma separated list of days of the week on which the alarm vibrates, e.g. MONDAY, TUESDAY.
        snooze_length: Minutes between alarms.
        snooze_count: Maximum snooze count.
      """
      return self.__post(f"/1/user/{self.user_id}/devices/tracker/{tracker_id}/alarms/{alarm_id}.json",
          params={
              "time": time, "enabled": enabled, "recurring": recurring, "weekDays": week_days, 
              "snoozeLength": snooze_length, "snoozeCount": snooze_count
          })
  
  def delete_alarm(self, tracker_id: int, alarm_id: int) -> None:
      """
      Deletes the user's device alarm entry with the given ID for a given device.

      Parameters:
        tracker_id: The ID of the tracker for which data is returned. The tracker-id value is found via the Get Devices endpoint.
        alarm_id: The ID of the alarm to be updated. The alarm-id value is found in the response of the Get Activity endpoint.
      """
      return self.__delete(f"/1/user/{self.user_id}/devices/tracker/{tracker_id}/alarms/{alarm_id}.json", is_json=False)
  
  """
  Food and Water
  
  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/food-logging/
  """
  def food_locales(self):
      """
      Returns the food locales that the user may choose to search, log, and create food in.
      """
      return self.__get("/1/foods/locales.json")
  
  def food_goals(self):
      """
      Returns a user's current daily calorie consumption goal and/or foodPlan value in the format requested
      """
      return self.__get(f"/1/user/{self.user_id}/foods/log/goal.json")
  
  def update_food_goal(self, calories_or_intensity: Union[int, str], goal_type: str, personalized: str = "true"):
      """
      Updates a user's daily calories consumption goal or food plan and returns a response in the format requested.

      Parameters:
        calories_or_intensity: Manual calorie consumption goal or plan intensity (MAINTENANCE, EASIER, MEDIUM, KINDAHARD, or HARDER)
        goal_type: calories or intensity
        personalized: (optional) true or false
      """
      return self.__post(f"/1/user/{self.user_id}/foods/log/goal.json",
          params={goal_type: calories_or_intensity, "personalized": personalized})
  
  def food_logs(self, date: str):
      """
      Retreives a summary and list of a user's food log entries for a given day in the format requested.

      Parameters:
        date: The date of records to be returned. In the format yyyy-MM-dd.
      """
      return self.__get(f"/1/user/{self.user_id}/foods/log/date/{date}.json")
  
  def water_logs(self, date: str):
      """
      Retreives a summary and list of a user's water log entries for a given day in the requested using 
      units in the unit system that corresponds to the Accept-Language header provided.

      Parameters:
        date: The date of records to be returned. In the format yyyy-MM-dd.
      """
      return self.__get(f"/1/user/{self.user_id}/foods/log/water/date/{date}.json")
  
  def water_goal(self):
      """
      Retreives a summary and list of a user's water goal entries for a given day in the requested using 
      units in the unit system that corresponds to the Accept-Language header provided.
      """
      return self.__get(f"/1/user/{self.user_id}/foods/log/water/goal.json")
  
  def update_water_goal(self, target: int):
      """
      Updates a user's daily calories consumption goal or food plan and returns a response in the format requested.

      Parameters:
        target: The target water goal in the format X.X is set in unit based on locale.
      """
      return self.__post(f"/1/user/{self.user_id}/foods/log/water/goal.json",
          params={"target": target})
  
  def log_food(self, food_id_or_name: str, id_type: str, meal_type_id: str, unit_id: str, amount: str, date: str, favorite: bool = False, brand_name: str = "", calories: int = 0):
      """
      Creates food log entries for users with or without foodId value.

      Parameters:
        food_id_or_name: The food_id or the custom name of the food to be logged
        id_type: id or name
        meal_type_id: Meal types. 1=Breakfast; 2=Morning Snack; 3=Lunch; 4=Afternoon Snack; 5=Dinner; 7=Anytime.
        unit_id: The ID of units used. Typically retrieved via a previous call to Get Food Logs, Search Foods, or Get Food Units.
        amount: The amount consumed in the format X.XX in the specified unitId.
        date: Log entry date in the format yyyy-MM-dd.
        favorite: (optional) The true value will add the food to the user's favorites after creating the log entry; 
          while the false value will not. Valid only with foodId value.
        brand_name: (optional) Brand name of food. Valid only with foodName parameters.
        calories: (optional) Calories for this serving size. This is allowed with foodName parameter 
          (default to zero); otherwise it is ignored.
      """
      params = {id_type: food_id_or_name, "mealTypeId": meal_type_id, "unitId": unit_id, "amount": amount, "date": date}
      if id_type == "id":
          params["favorite"] = favorite
      if id_type == "name":
          params["brandName"] = brand_name
          params["calories"] = calories
      return self.__post(f"/1/user/{self.user_id}/foods/log.json",
          params=params)
  
  def delete_food_log(self, food_log_id: str):
      """
      Deletes a user's food log entry with the given ID.

      Parameters:
        food_log_id: The ID of the food log entry to be deleted.
      """
      return self.__delete(f"/1/user/{self.user_id}/foods/log/{food_log_id}.json")
  
  def edit_food_log(self, food_log_id: str, meal_type_id: str, unit_id: str, amount: str):
      """
      The Edit Food Log endpoint changes the quantity or calories consumed for a user's food log entry with the given Food Log ID.

      Parameters:
        food_log_id: The ID of the food log entry to be edited.
        meal_type_id: Meal types. 1=Breakfast; 2=Morning Snack; 3=Lunch; 4=Afternoon Snack; 5=Dinner; 7=Anytime.
        unit_id: The ID of units used. Typically retrieved via a previous call to Get Food Logs, Search Foods, or Get Food Units.
        amount: The amount consumed in the format X.XX in the specified unitId.
      """
      return self.__post(f"/1/user/{self.user_id}/foods/log/{food_log_id}.json",
          params={"mealTypeId": meal_type_id, "unitId": unit_id, "amount": amount})
  
  def log_water(self, date: str, amount: int, unit: str = "fl oz"):
      """
      Creates a log entry for water using units in the unit systems that corresponds to the Accept-Language header provided.

      Parameters:
        date: The date of records to be returned in the format yyyy-MM-dd.
        amount: The amount consumption in the format X.XX and in the specified waterUnit or in the 
          unit system that corresponds to the Accept-Language header provided.
        unit: (optional) Water measurement unit; ml, fl oz, or cup
      """
      return self.__post(f"/1/user/{self.user_id}/foods/log/water.json",
          params={"date": date, "amount": amount, "unit": unit})
  
  def delete_water_log(self, water_log_id: str):
      """
      Deletes a user's water log entry with the given ID.

      Parameters:
        water_log_id: The ID of the waterUnit log entry to be deleted.
      """
      return self.__delete(f"/1/user/{self.user_id}/foods/log/water/{water_log_id}.json")
  
  def update_water_log(self, water_log_id: str, amount: str, unit: str = "fl oz"):
      """
      Updates a user's water log entry with the given ID.

      Parameters:
        water_log_id: The ID of the waterUnit log entry to be updated
        amount: Amount consumed; in the format X.X and in the specified waterUnit or in the 
          unit system that corresponds to the Accept-Language header provided.
        unit: (optional) Water measurement unit. 'ml', 'fl oz', or 'cup'.
      """
      return self.__post(f"/1/user/{self.user_id}/foods/log/water/{water_log_id}.json",
          params={"amount": amount, "unit": unit})
  
  def favorite_foods(self):
      """
      Returns a list of a user's favorite foods in the format requested. A favorite food in the list 
      provides a quick way to log the food via the Log Food endpoint.
      """
      return self.__get(f"/1/user/{self.user_id}/foods/log/favorite.json")
  
  def frequent_foods(self):
      """
      Returns a list of a user's frequent foods in the format requested. A frequent food in the list 
      provides a quick way to log the food via the Log Food endpoint.
      """
      return self.__get(f"/1/user/{self.user_id}/foods/log/frequent.json")
  
  def add_favorite_food(self, food_id: str):
      """
      Updates a user's daily activity goals and returns a response using units in the unit system which 
      corresponds to the Accept-Language header provided.

      Parameters:
        food_id: The ID of the food to be added to user's favorites.
      """
      return self.__post(f"/1/user/{self.user_id}/foods/log/favorite/{food_id}.json")
  
  def delete_favorite_food(self, food_id: str):
      """
      Deletes a food with the given ID to the user's list of favorite foods.

      Parameters:
        food_id: The ID of the food to be deleted from user's favorites.
      """
      return self.__delete(f"/1/user/{self.user_id}/foods/log/favorite/{food_id}.json")
  
  def meals(self):
      """
      Returns a list of meals created by user in the user's food log in the format requested. 
      User creates and manages meals on the Food Log tab on the website.
      """
      return self.__get(f"/1/user/{self.user}/meals.json")
  
  def create_meal(self, name: str, description: str, food_id: str, unit_id: str, amount: str):
      """
      Creates a meal with the given food contained in the post body.

      Parameters:
        name: Name of the meal.
        description: Short description of the meal.
        food_id: ID of the food to be included in the meal.
        unit_id: ID of units used. Typically retrieved via a previous call to Get Food Logs, Search Foods, or Get Food Units.
        amount: Amount consumed; in the format X.XX, in the specified unitId.
      """
      return self.__post(f"/1/user/{self.user}/meals.json",
          params={"name": name, "description": description, "foodId": food_id, "unitId": unit_id, "amount": amount})
  
  def edit_meal(self, meal_id: str, name: str, description: str, food_id: str, unit_id: str, amount: str):
      """
      Replaces an existing meal with the contents of the request. The response contains the updated meal.

      Parameters:
        meal_id: Id of the meal to edit.
        name: Name of the meal.
        description: Short description of the meal.
        food_id: ID of the food to be included in the meal.
        unit_id: ID of units used. Typically retrieved via a previous call to Get Food Logs, Search Foods, or Get Food Units.
        amount: Amount consumed; in the format X.XX, in the specified unitId.
      """
      return self.__post(f"/1/user/{self.user_id}/meals/{meal_id}.json",
          params={"name": name, "description": description, "foodId": food_id, "unitId": unit_id, "amount": amount})
  
  def delete_meal(self, meal_id: str):
      """
      Deletes a user's meal with the given meal id.

      Parameters:
        meal_id: Id of the meal to delete.
      """
      return self.__delete(f"/1/user/{self.user_id}/meals/{meal_id}.json")
  
  def recent_foods(self):
      """
      Returns a list of a user's frequent foods in the format requested. A frequent food 
      in the list provides a quick way to log the food via the Log Food endpoint.
      """
      return self.__get(f"/1/user/{self.user_id}/foods/log/recent.json")
  
  def create_food(self, name: str, default_food_measurement_unit_id: str, default_serving_size: str, calories: str, form_type: str = "", description: str = ""):
      """
      Creates a new private food for a user and returns a response in the format requested. The created food 
      is found via the Search Foods call.

      Parameters:
        name: The food name.
        default_food_measurement_unit_id: The ID of the default measurement unit. Full list of 
          units can be retrieved via the Get Food Units endpoint.
        default_serving_size: The size of the default serving. Nutrition values should be provided for this serving size.
        calories: The calories in the default serving size.
        form_type: (optional) Form type; LIQUID or DRY.
        description: The description of the food.
      """
      return self.__post(f"/1/user/{self.user_id}/foods.json",
          params={"name": name, "defaultFoodMeasurementUnitId": default_food_measurement_unit_id, "defaultServingSize": default_serving_size,
              "calories": calories, "formType": form_type, "description": description})
  
  def delete_custom_food(self, food_id: str):
      """
      Deletes custom food for a user and returns a response in the format requested.

      Parameters:
        food_id: The ID of the food to be deleted.
      """
      return self.__delete(f"/1/user/{self.user_id}/foods/{food_id}.json")
  
  def food(self, food_id: str):
      """
      Returns the details of a specific food in the Fitbit food databases or a private food 
      that an authorized user has entered in the format requested.

      Parameters:
        food_id: The ID of the food.
      """
      return self.__get(f"/1/foods/{food_id}.json")
  
  def food_units(self):
      """Returns a list of all valid Fitbit food units in the format requested."""
      return self.__get(f"/1/foods/units.json")
  
  def search_foods(self, query: str):
      """
      Returns a list of public foods from the Fitbit food database and private food the user created in the format requested.

      Parameters:
        query: The URL-encoded search query.
      """
      return self.__get("/1/foods/search.json",
          params={"query": query})
  
  """
  Food and Water Time Series

  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/food-logging/#food-or-water-time-series
  """
  def food_or_water_time_series(self, base_date: str, end_or_period: str, resource_path: str = "caloriesIn"):
      """
      Updates a user's daily activity goals and returns a response using units in the unit system which corresponds 
      to the Accept-Language header provided.

      Parameters: 
        base_date: If an end date is provided, base_date refers to the start date. If a period is
          provided instead, base_date will be the last date of that period
        end_or_period: A date in the format yyyy-MM-dd or one of the following periods:
          1d, 7d, 30d, 1w, 1m, 3m, 6m, 1y, or max
        resource_path: (optional) caloriesIn, water
      """
      return self.__get(f"/1/user/{self.user_id}/foods/log/{resource_path}/date/{base_date}/{end_or_period}.json")

  """
  Friends

  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/friends/
  """
  def friends(self):
    """
    Returns data of a user's friends in the format requested using units in the unit system which 
    corresponds to the Accept-Language header provided.
    """
    return self.__get(f"/1.1/user/{self.user_id}/friends.json")

  def friends_leaderboard(self):
    """
    Returns data of a user's friends in the format requested using units in the unit system which 
    corresponds to the Accept-Language header provided.
    """
    return self.__get(f"/1.1/user/{self.user_id}/leaderboard/friends.json")

  def friend_invitations(self):
    """Returns a list of invitations to become friends with a user in the format requested."""
    return self.__get(f"/1.1/user/{self.user_id}/friends/invitations.json")

  def invite_friends(self, user_id: str, id_type: str):
    """
    Creates an invitation to become friends with the authorized user. Either invitedUserEmail 
    or invitedUserId needs to be provided.

    Parameters:
      user_id: Email or encoded id of the user to invite
      id_type: email or id
    """
    return self.__post(f"/1.1/user/{self.user_id}/friends/invitations",
        params={f"invitedUser{id_type.capitalize()}": user_id})

  def friend_invitation(self, from_user_id: str, accept: str):
    """
    Accepts or rejects an invitation to become friends wit inviting user.
    
    Parameters:
      from_user_id: The encoded ID of a user from which to accept or reject invitation.
      accept: Accept or reject invitation; true or false.
    """
    return self.__post(f"/1.1/user/{self.user_id}/friends/invitations/{from_user_id}",
        params={"accept": accept})

  """
  Heart Rate Intraday Time Series

  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/heart-rate/#get-heart-rate-intraday-time-series
  """
  def heart_rate_intraday(self, base_date: str, end_or_1d: str, detail_level: str, start_time: str = None, end_time: str = None):
    """
    Returns the intraday time series for a given resource in the format requested. If your application has the 
    appropriate access, your calls to a time series endpoint for a specific day (by using start and end dates 
    on the same day or a period of 1d), the response will include extended intraday values with a one-minute 
    detail level for that day. Unlike other time series calls that allow fetching data of other users, intraday 
    data is available only for and to the authorized user.

    Parameters:
      base_date: The date in the format of yyyy-MM-dd or today.
      end_or_1d: The end date in the format of yyyy-MM-dd or 1d for a 1 day time period
      detail_level: The number of data points to include either 1sec or 1min.
      start_time: (optional) The start of the period in the format of HH:mm.
      end_time: (optional) The end time of the period in the format of HH:mm.
    """
    if start_time is not None and end_time is not None:
        time = f"/time/{start_time}/{end_time}"
    else:
        time = ""
    return self.__get(f"/1/user/{self.user_id}/activities/heart/date/{base_date}/{end_or_1d}/{detail_level}{time}.json")

  """
  Heart Rate Time Series

  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/heart-rate/#heart-rate-time-series
  """
  def heart_rate_time_series(self, base_date: str, end_or_period: str):
    """
    Returns the time series data in the specified range for a given resource in the format requested 
    using units in the unit systems that corresponds to the Accept-Language header provided.

    Parameters: 
      base_date: If an end date is provided, base_date refers to the start date. If a period is
        provided instead, base_date will be the last date of that period
      end_or_period: A date in the format yyyy-MM-dd or one of the following periods:
        1d, 7d, 30d, 1w, 1m, 3m, 6m, 1y, or max
    """
    return self.__get(f"/1/user/{self.user_id}/activities/heart/date/{base_date}/{end_or_period}.json")

  """
  Sleep

  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/sleep/
  """
  def delete_sleep_log(self, log_id: str):
    """
    Deletes a user's sleep log entry with the given ID.

    Parameters:
      log_id: The ID of the sleep log to be deleted.
    """
    return self.__delete(f"/1.2/user/{self.user_id}/sleep/{log_id}.json")

  def sleep_log(self, date: str):
    """
    The Get Sleep Logs by Date endpoint returns a summary and list of a user's sleep 
    log entries (including naps) as well as detailed sleep entry data for a given day.

    Parameters:
      date: The date of records to be returned. In the format yyyy-MM-dd.
    """
    return self.__get(f"/1.2/user/{self.user_id}/sleep/date/{date}.json")

  def sleep_logs_range(self, base_date: str, end_date: str):
    """
    The Get Sleep Logs by Date Range endpoint returns a list of a user's sleep log entries 
    (including naps) as well as detailed sleep entry data for a given date range 
    (inclusive of start and end dates).

    Parameters:
      base_date: The date of records to be returned. In the format yyyy-MM-dd.
      end_date: The date of records to be returned. In the format yyyy-MM-dd.
    """
    return self.__get(f"/1.2/user/{self.user_id}/date/{base_date}/{end_date}.json")

  def sleep_logs_list(self, date: str, date_type: str, sort: str, offset: int, limit: int):
    """
    The Get Sleep Logs List endpoint returns a list of a user's sleep logs (including naps) 
    before or after a given day with offset, limit, and sort order.

    Parameters:
      date: The before or after date (type specified in the date_type parameter)
      date_type: before or after
      sort: The sort order of entries by date asc (ascending) or desc (descending).
      offset: The offset number of entries.
      limit: The maximum number of entries returned (maximum;100).
    """
    return self.__get(f"/1.2/user/{self.user_id}/sleep/list.json",
      params={f"{date_type}Date": date, "sort": sort, "offset": offset, "limit": limit})

  def sleep_goal(self):
    """Returns the user's sleep goal."""
    return self.__get(f"/1.2/user/{self.user_id}/sleep/goal.json")

  def update_sleep_goal(self, min_duration: str):
    """
    Create or update the user's sleep goal and get a response in the JSON format.

    Parameters:
      min_duration: Duration of sleep goal.
    """
    return self.__post(f"/1.2/user/{self.user_id}/sleep/goal.json",
      params={"minDuration": min_duration})

  def log_sleep(self, start_time: str, duration: int, date: str):
    """
    Creates a log entry for a sleep event and returns a response in the format requested.

    Parameters: 
      start_time: Start time includes hours and minutes in the format HH:mm.
      duration: Duration in milliseconds.
      date: Log entry in the format yyyy-MM-dd.
    """
    return self.__post(f"/1.2/user/{self.user_id}/sleep.json",
      params={"startTime": start_time, "duration": duration, "date": date})

  """
  Subscriptions

  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/subscriptions/
  """
  def subscriptions(self, collection_path: str):
    """
    Retreives a list of a user's subscriptions for your application in the format requested. 
    You can either fetch subscriptions for a specific collection or the entire list of 
    subscriptions for the user. For best practice, make sure that your application maintains 
    this list on your side and use this endpoint only to periodically ensure data consistency.

    Parameters:
      collection_path: This is the resource of the collection to receive notifications from (foods, 
        activities, sleep, or body). If not present, subscription will be created for all collections. 
        If you have both all and specific collection subscriptions, you will get duplicate notifications 
        on that collections' updates. Each subscriber can have only one subscription for a specific 
        user's collection.
    """
    return self.__get(f"/1/user/{self.user_id}/{collection_path}/apiSubscriptions.json")

  def add_subscription(self, collection_path: str, subscription_id: str):
    """
    Adds a subscription in your application so that users can get notifications 
    and return a response in the format requested. The subscription-id value 
    provides a way to associate an update with a particular user stream in your application.

    Parameter:
      collection_path: This is the resource of the collection to receive notifications from 
        (foods, activities, sleep, or body). If not present, subscription will be created for 
        all collections. If you have both all and specific collection subscriptions, you will 
        get duplicate notifications on that collections' updates. Each subscriber can have only 
        one subscription for a specific user's collection.
      subscription_id: This is the unique ID of the subscription created by the API client 
        application. Each ID must be unique across the entire set of subscribers and collections. 
        The Fitbit servers will pass this ID back along with any notifications about the user 
        indicated by the user parameter in the URL path.
    """
    return self.__post(f"/1/user/{self.user_id}/{collection_path}/apiSubscriptions/{subscription_id}.json")

  def delete_subscription(self, collection_path: str, subscription_id: str):
    return self.__delete(f"/1/user/{self.user_id}/{collection_path}/apiSubscriptions/{subscription_id}.json")

  """
  User

  Full documentation: 
    https://dev.fitbit.com/build/reference/web-api/user/
  """
  def badges(self):
    """
    This is the unique ID of the subscription created by the API client application. 
    Each ID must be unique across the entire set of subscribers and collections. The 
    Fitbit servers will pass this ID back along with any notifications about the user 
    indicated by the user parameter in the URL path.
    """
    return self.__get(f"/1/user/{self.user_id}/badges.json")

  def profile(self):
    """
    Returns a user's profile. The authenticated owner receives all values. 
    However, the authenticated user's access to other users' data is subject 
    to those users' privacy settings. Numerical values are returned in the 
    unit system specified in the Accept-Language header.
    """
    return self.__get(f"/1/user/{self.user_id}/profile.json")

  def update_profile(self, params):
    """
    TODO
    """
    return self.__post(f"/1/user/{self.user_id}/profile.json",
      params=params)
