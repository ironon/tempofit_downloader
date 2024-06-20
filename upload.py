import json
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
from google.resumable_media import requests, common
import os
import ffmpeg
import m3u8
import requests
import datetime
import mder
creds = json.load(open('key.json'))

def dl_m3u8(dl_url, filepath):
    try:
        stream = ffmpeg.input(dl_url)
        stream = ffmpeg.output(stream, f'{filepath}.mp4')
        ffmpeg.run(stream)
    except Exception as e:
        print(e)

credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    creds
)
client = storage.Client(credentials=credentials, project='obsidian')
bucket = client.get_bucket('tempo_very_legit')

def upload_file(file_path, new_file_name: str):
    # print(file_path)
    saveName = "".join(char for char in new_file_name if char.isalnum())
    command = f"m4 {file_path} --auto-select --save-name {saveName}"
    os.chdir(r"C:\Users\875497\Documents\tempo_downloader\m4")
    os.system(command)
    print(f"ffmpeg -i {saveName}.mp4 -i {saveName}.eng.m4a -c:v copy -c:a aac output.mp4")
    os.system(f"ffmpeg -i {saveName}.mp4 -i {saveName}.eng.m4a -c:v copy -c:a aac {saveName}_audio.mp4")

    blob = bucket.blob(saveName + '_audio.mp4')
    blob.chunk_size = 5 * 1024 * 1024  # Set chunk size to 5MB
    with open(f"{saveName}.mp4", "rb") as file_obj:
        blob.upload_from_file(
            file_obj,
            content_type='video/mp4',
            num_retries=5,
            client=client,
            
        )
    #copy m4.exe to ../, delete everything in ./, move m4.exe back to ./, delete m4.exe
    ## remember that we are on windows
    os.system("move m4.exe ..")
    ## do del *, no confirmation, recursive
    os.system("del /Q *")
    os.system("move ..\m4.exe .")
    os.system("del ..\m4.exe")
    

    return blob.public_url


def get_mass_of_tempo_data():

    url = "https://api.trainwithpivot.com/v1/graphql"
    ## if tempo_data exists, and it is less than 24 hours old, return it. use file.mtime

    if os.path.exists('tempo_data.json'):
        tempo_data = json.load(open('tempo_data.json'))
        if datetime.datetime.now() < datetime.datetime.fromtimestamp(os.path.getmtime('tempo_data.json')) + datetime.timedelta(hours=24):
            return tempo_data
        
    payload = "{\"query\":\"query HomeScreenData(\\n  $userId: UUID!\\n  $scheduledWorkoutsFilter: ScheduledWorkoutFilter!\\n) {\\n  getUserTrainingPlan(userId: $userId) {\\n    __typename\\n    ...UserTrainingPlanFragment\\n  }\\n  getUserBodyReadiness(userId: $userId) {\\n    overallReadiness {\\n      readinessPct\\n      readinessState\\n    }\\n    readinessByMuscleGroup {\\n      muscleGroup\\n      readinessPct\\n      readinessState\\n    }\\n  }\\n  currentUser {\\n    scheduledWorkouts(filters: $scheduledWorkoutsFilter, first: 10) {\\n      edges {\\n        node {\\n          __typename\\n          ...HomeScheduledWorkoutFragment\\n        }\\n      }\\n    }\\n    completedWorkouts(first: 100, sort: START_TIME_DESC) {\\n      edges {\\n        node {\\n          __typename\\n          ...ListItemCompletedWorkoutFragment\\n        }\\n      }\\n    }\\n    currentWorkoutPrograms(first: 5, sort: LAST_COMPLETED_WORKOUT_TIME_DESC) {\\n      edges {\\n        node {\\n          nextPlannedWorkout {\\n            index\\n            plannedWorkoutProgram {\\n              dbId\\n              workoutProgram {\\n                dbId\\n                title\\n                nextClassSession {\\n                  dbId\\n                  title\\n                  thumbnailUrl\\n                  duration\\n                  activity\\n                }\\n              }\\n            }\\n          }\\n        }\\n      }\\n    }\\n  }\\n}\\nfragment TrainingPlanRecommendedClassSessionFragment on ClassSessionNode {\\n  dbId\\n  classType\\n  duration\\n  instructor {\\n    firstName\\n  }\\n  potentialClassAchievementMetrics {\\n    achievementMetricType\\n    achievementMetricValue\\n  }\\n}\\nfragment TrainingPlanIntentFragment on TrainingPlanIntent {\\n  dbId\\n  greeting\\n  greetingHighlights\\n  title\\n  imageUrl\\n  recommendedClassSession {\\n    __typename\\n    ...TrainingPlanRecommendedClassSessionFragment\\n  }\\n  muscleGroupSets {\\n    muscleGroup\\n    sets\\n    isFocus\\n  }\\n}\\nfragment TrainingPlanCompletedWorkoutFragment on WorkoutNode {\\n  dbId\\n  endTime\\n  volume\\n  calories\\n  intensityMinutes\\n  classSession {\\n    dbId\\n    title\\n    thumbnailUrl\\n    duration\\n  }\\n}\\nfragment TrainingPlanTargetWeeklyProgressFragment on TargetWeeklyProgress {\\n  progress\\n  target\\n  targetTypeLabel\\n  targetType\\n}\\nfragment TrainingPlanDetailsFragment on TrainingPlan {\\n  id\\n  title\\n  shortDescription\\n  longDescription\\n  weeks\\n  trainer {\\n    id\\n    firstName\\n    lastName\\n    fullName\\n    trainerFaceImageUrl\\n  }\\n  focus\\n  goodForGoal\\n  imageUrl\\n  daysRecommended\\n  daysRequired\\n  minWorkoutMinutes\\n  maxWorkoutMinutes\\n  objectives {\\n    description\\n    icon\\n  }\\n  primaryMuscleGroups\\n  aestheticBenefit\\n  weeklyTargets {\\n    target\\n    value\\n  }\\n}\\nfragment TrainingPlanTargetsFieldsFragment on TrainingPlanTargetRow {\\n  fields {\\n    title\\n    subtitle\\n    value\\n    unit\\n  }\\n}\\nfragment UserTrainingPlanFragment on UserTrainingPlan {\\n  defaultTrainingPlanIntensity\\n  state\\n  weeks {\\n    status\\n    state\\n    trainingPlanIntents {\\n      __typename\\n      ...TrainingPlanIntentFragment\\n    }\\n    muscleGroupWeeklyProgress {\\n      muscleGroup\\n      muscleGroupLabel\\n      progress\\n      target\\n    }\\n    completedWorkouts {\\n      __typename\\n      ...TrainingPlanCompletedWorkoutFragment\\n    }\\n    targetWeeklyProgress {\\n      __typename\\n      ...TrainingPlanTargetWeeklyProgressFragment\\n    }\\n  }\\n  trainingPlan {\\n    __typename\\n    ...TrainingPlanDetailsFragment\\n  }\\n  isRecovering\\n  targetFields {\\n    __typename\\n    ...TrainingPlanTargetsFieldsFragment\\n  }\\n}\\nfragment HomeScheduledWorkoutFragment on ScheduledWorkoutNode {\\n  scheduledAt\\n  classSession {\\n    dbId\\n    title\\n    thumbnailUrl\\n    duration\\n  }\\n}\\n\\n\\nfragment ListItemCompletedWorkoutFragment on WorkoutNode {\\n  dbId\\n  endTime\\n\\treps,\\n\\tintensityMinutes,\\n\\tperformanceSummary {\\n\\t\\t__typename,\\n\\t\\tcircuitName,\\n\\t\\tcircuitSets {\\n\\t\\t\\texerciseId,\\n\\t\\t\\texerciseName,\\n\\t\\t\\tweight,\\n\\t\\t\\treps,\\n\\t\\t\\t\\n\\t\\t}\\n\\t\\n\\t},\\n  classSession {\\n    dbId\\n    title,\\n\\t\\tcreator {\\n\\t\\t\\tfullName\\n\\t\\t},\\n    thumbnailUrl\\n\\t\\tvideoUrl,\\n    duration\\n  }\\n}\\n\",\"operationName\":\"HomeScreenData\",\"variables\":\"{\\n\\t\\\"userId\\\": \\\"3582e853-80bb-4bfe-bbad-f6cb3d05cf1c\\\",\\n\\t\\\"scheduledWorkoutsFilter\\\": {\\n\\t\\t\\\"excludeCompleted\\\": true,\\n\\t\\t\\\"scheduledBetween\\\": {\\n\\t\\t\\t\\\"startTime\\\": \\\"2024-05-04T00:00Z\\\",\\n\\t\\t\\t\\\"endTime\\\": \\\"2024-05-05T23:59:59.999999999Z\\\"\\n\\t\\t}\\n\\t}\\n}\"}"
    headers = {
        "User-Agent": "insomnia/9.1.0",
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTQ5MzA4MDUsImlhdCI6MTcxNDg0NDQwNSwic3ViIjoiMzU4MmU4NTMtODBiYi00YmZlLWJiYWQtZjZjYjNkMDVjZjFjIiwicm9sZSI6IkN1c3RvbWVyIiwiY2xpZW50X2lkIjoiYWFkMDYzNWItMGY0OS00YThhLWJmMGYtYjdjYjA5ZDhiOWE4Iiwic2NvcGUiOm51bGwsImZpcnN0X25hbWUiOiJEYXZpZCJ9.Jnt3txkcYnvNaobDvVaMIsZFsirGWGHw1PrTZpMd4zw"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    data = response.json()

    with open('tempo_data.json', 'w') as f:
        json.dump(data, f)
    return data
def video_already_uploaded(video_url):
    for blob in bucket.list_blobs():
        # print("checking " + blob.public_url + " for " + video_url)
        if "".join(char for char in video_url if char.isalnum()) in blob.public_url:
            print(video_url + " already uploaded ✅" )
            return True
    return False

def upload_all_videos(data):
    for workout in data["data"]["currentUser"]["completedWorkouts"]["edges"]:
        video_url = workout["node"]["classSession"]["videoUrl"]
       
        ## check if video is already uploaded
        if not video_already_uploaded(workout["node"]["classSession"]["title"] + '.mp4'):
            print("uploading " + workout["node"]["classSession"]["title"] + '.mp4')
            new_url = upload_file(video_url, workout["node"]["classSession"]["title"] + '.mp4')
            print(new_url)
            # print('uploaded')
    
if __name__ == "__main__":
    print("getting tempo data")
    data = get_mass_of_tempo_data()
    print("uploading videos")
    upload_all_videos(data)
    print('done')
