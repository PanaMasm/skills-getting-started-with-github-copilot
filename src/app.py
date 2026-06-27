"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

def normalize_participant(participant):
    if isinstance(participant, dict):
        email = participant.get("email") or participant.get("name") or ""
        name = participant.get("name") or email
        return {"email": email, "name": name}

    email = str(participant)
    return {"email": email, "name": email}


def normalize_activity(activity):
    activity["participants"] = [normalize_participant(participant) for participant in activity.get("participants", [])]


# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}

# Additional activities
activities.update({
    "Soccer Team": {
        "description": "Competitive soccer training and matches",
        "schedule": "Mondays, Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Team practices and inter-school games",
        "schedule": "Tuesdays, Thursdays, 4:30 PM - 6:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "sophia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore drawing, painting, and mixed media",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu"]
    },
    "Drama Society": {
        "description": "Theatre production, acting workshops, and performances",
        "schedule": "Fridays, 3:30 PM - 6:00 PM",
        "max_participants": 25,
        "participants": ["mason@mergington.edu"]
    },
    "Debate Club": {
        "description": "Practice public speaking and competitive debating",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Prepare for science and engineering competitions",
        "schedule": "Tuesdays, 3:30 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["sophia@mergington.edu"]
    }
})

for activity in activities.values():
    normalize_activity(activity)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, name: str | None = None):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if any(normalize_participant(participant)["email"] == email for participant in activity["participants"]):
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    display_name = name or email

    # Add student
    activity["participants"].append({"email": email, "name": display_name})
    return {"message": f"Signed up {display_name} for {activity_name}"}


@app.delete("/activities/{activity_name}/participants/{email}")
def unregister_participant(activity_name: str, email: str):
    """Remove a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    participant_index = next(
        (index for index, participant in enumerate(activity["participants"]) if normalize_participant(participant)["email"] == email),
        None,
    )

    if participant_index is None:
        raise HTTPException(status_code=404, detail="Participant not found")

    activity["participants"].pop(participant_index)
    return {"message": f"Removed {email} from {activity_name}"}
