import streamlit as st
from observability import init_observability
from ai import ask_ai, get_macros
from profiles import create_profile, get_notes, get_profile
from form_submit import update_personal_info, add_note, delete_note

st.set_page_config(
    page_title="AI Fitness Coach",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_observability("ai-workflow-app")


@st.fragment()
def personal_data_form():
    with st.form("personal_data"):
        st.subheader("Profile")
        profile = st.session_state.profile

        name = st.text_input("Name", value=profile["general"].get("name", ""))
        age = st.number_input("Age", min_value=1, max_value=120, step=1, value=profile["general"].get("age", 25))
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, step=0.1, value=float(profile["general"].get("weight", 70.0)))
        height = st.number_input("Height (cm)", min_value=0.0, max_value=250.0, step=0.1, value=float(profile["general"].get("height", 170.0)))
        genders = ["Male", "Female", "Other"]
        gender = st.radio("Gender", genders, index=genders.index(profile["general"].get("gender", "Male")))
        activities = [
            "Sedentary",
            "Lightly Active",
            "Moderately Active",
            "Very Active",
            "Super Active",
        ]
        activity_level = st.selectbox(
            "Activity Level",
            activities,
            index=activities.index(profile["general"].get("activity_level", "Sedentary")),
        )

        if st.form_submit_button("Save Profile"):
            st.session_state.profile = update_personal_info(
                profile,
                "general",
                name=name,
                weight=weight,
                height=height,
                gender=gender,
                age=age,
                activity_level=activity_level,
            )
            st.success("Profile updated.")


@st.fragment()
def goals_form():
    profile = st.session_state.profile
    with st.form("goals_form"):
        st.subheader("Goals")
        goals = st.multiselect(
            "Select your goals",
            ["Muscle Gain", "Fat Loss", "Stay Active"],
            default=profile.get("goals", ["Muscle Gain"]),
        )

        if st.form_submit_button("Save Goals"):
            if goals:
                st.session_state.profile = update_personal_info(profile, "goals", goals=goals)
                st.success("Goals updated.")
            else:
                st.warning("Please select at least one goal.")


@st.fragment()
def macros():
    profile = st.session_state.profile
    st.subheader("Nutrition Targets")

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Generate with AI", type="primary"):
            result = get_macros(profile.get("general"), profile.get("goals", []))
            if isinstance(result, dict) and result.get("error"):
                st.error(result.get("error"))
            else:
                profile["nutrition"] = result
                st.session_state.profile = profile
                st.success("Targets generated.")

    with st.form("nutrition_form"):
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            calories = st.number_input("Calories", min_value=0, step=1, value=profile["nutrition"].get("calories", 0))
        with col_b:
            protein = st.number_input("Protein (g)", min_value=0, step=1, value=profile["nutrition"].get("protein", 0))
        with col_c:
            fat = st.number_input("Fat (g)", min_value=0, step=1, value=profile["nutrition"].get("fat", 0))
        with col_d:
            carbs = st.number_input("Carbs (g)", min_value=0, step=1, value=profile["nutrition"].get("carbs", 0))

        if st.form_submit_button("Save Targets"):
            st.session_state.profile = update_personal_info(
                profile,
                "nutrition",
                protein=protein,
                calories=calories,
                fat=fat,
                carbs=carbs,
            )
            st.success("Targets saved.")


@st.fragment()
def notes():
    st.subheader("Notes")
    for i, note in enumerate(st.session_state.notes):
        cols = st.columns([5, 1])
        with cols[0]:
            st.text(note.get("text"))
        with cols[1]:
            if st.button("Delete", key=f"delete-{i}"):
                delete_note(note.get("_id"))
                st.session_state.notes.pop(i)
                st.rerun()

    new_note = st.text_input("Add a new note")
    if st.button("Add Note"):
        if new_note:
            note = add_note(new_note, st.session_state.profile_id)
            st.session_state.notes.append(note)
            st.rerun()


@st.fragment()
def ask_ai_func():
    st.subheader("Ask AI")
    user_question = st.text_area("Ask a question", height=120)
    if st.button("Ask AI", type="primary"):
        with st.spinner("Thinking..."):
            result = ask_ai(st.session_state.profile, user_question)
            st.write(result)


def main():
    st.title("AI Fitness Coach")
    st.caption("Personalized nutrition targets and contextual training advice.")

    if "profile" not in st.session_state:
        profile_id = 1
        profile = get_profile(profile_id)
        if not profile:
            profile_id, profile = create_profile(profile_id)

        st.session_state.profile = profile
        st.session_state.profile_id = profile_id

    if "notes" not in st.session_state:
        st.session_state.notes = get_notes(st.session_state.profile_id)

    tab_profile, tab_nutrition, tab_notes, tab_ask = st.tabs([
        "Profile",
        "Nutrition",
        "Notes",
        "Ask AI",
    ])

    with tab_profile:
        personal_data_form()
        goals_form()

    with tab_nutrition:
        macros()

    with tab_notes:
        notes()

    with tab_ask:
        ask_ai_func()


if __name__ == "__main__":
    main()

