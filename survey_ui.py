import streamlit as st
import pandas as pd

questions_and_suggestions = {
    "Some of my favorite books include": "1984, The Catcher in The Rye, Dune",
    "I want to be known as someone who is": "intelligent, cultured, quirky",
    "I am in the mood for": "adventure, romance, self-improvement",
    "Fictional characters I want to be like": "Sherlock, Thanos, Beth Harmon",
    "Real-world people I want to be like": "Roger Federer, Agatha Christie, Barack Obama"
}

# Initialize session state
if "response_dict" not in st.session_state:
    st.session_state.response_dict = {q: [] for q in questions_and_suggestions.keys()}
if "response_input" not in st.session_state:
    st.session_state.response_input = ""
if "question_suggestion" not in st.session_state:
    st.session_state.question_suggestion = list(questions_and_suggestions.keys())[0]

st.write(st.session_state.response_dict)

def add_response():
    response = st.session_state.response_input.strip()
    response_list = st.session_state.response_dict[st.session_state.question_suggestion]

    if response:
        # Remove if duplicate to move it to most recent
        if response in response_list:
            response_list.remove(response)
        elif len(response_list) == 5:
           response_list.pop(0)
        response_list.append(response)
        st.session_state.response_input = ""  # Clear input

def clear_responses():
    response_list = st.session_state.response_dict[st.session_state.question_suggestion]
    response_list.clear()

def remove_last_response():
    response_list = st.session_state.response_dict[st.session_state.question_suggestion]
    if response_list:
        response_list.pop()

st.set_page_config(page_title="Designing Survey", layout="wide")

left_column, breaker, col_recommend = st.columns([4.5, 0.5, 6])

with left_column:

    with st.expander("📚 Book Personality & Genre Survey"):
        
        name_col, gender_col = st.columns([2.5,3])
        with name_col:
            name = st.text_input("Name:", key="name")

        with gender_col:
            reading_preference = st.radio(
                "I prefer:",
                options=["Fiction", "Non-fiction", "Both"],
                horizontal=True,
                key="reading_preference"
            )

        god_col1, god_col2 = st.columns([2.5,3])
        
        curr_responses = st.session_state.response_dict[st.session_state.question_suggestion]

        with god_col1:
            question_suggestion = st.selectbox(
                "About me:",
                options=questions_and_suggestions.keys(),
                key="question_suggestion"
            )

            # Display the books as a formatted string
            if curr_responses:
                response_text = ""
                for i, response in enumerate(curr_responses, 1):
                    response_text += f"{i}. {response}\n"
                st.write(response_text)
            else:
                st.write("No responses yet")

        with god_col2:
            specific_suggestion = questions_and_suggestions[st.session_state["question_suggestion"]]

            response_input = st.text_input(
                f"Examples: {specific_suggestion}", 
                key="response_input",
                on_change=add_response,
                label_visibility="visible"
            )

            undo_col, clear_col = st.columns([1, 5])
            with undo_col:
                if curr_responses:
                    st.button("Undo", on_click=remove_last_response)
            with clear_col:
                if curr_responses:
                    st.button("Clear", on_click=clear_responses)


def generate_genre_prompt():
    name = st.session_state.get("name", "").strip() or "Unknown"
    genre_pref = st.session_state.get("reading_preference", "Unknown")
    if genre_pref == "Both":
        genre_pref = "Both fiction and non-fiction"

    question = st.session_state.get("question_suggestion", "N/A")
    
    responses = ""
    if question in st.session_state.response_dict:
        responses = st.session_state.response_dict[question]

    response_text = ", ".join(responses) if responses else "No responses given"

    prompt = f'''Use the following information about the user to generate predictions 
    on his/her book genre preferences on a scale of 0–50 in the following Python dict format:

example_dict = {{
    'Classics': 25,  
    'Contemporary': 7,
    'Fantasy': 17,
    'Historical Fiction': 7,
    'Horror': 2,
    'Mystery': 2,
    'Romance': 7,
    'Science Fiction': 15,
    'Young Adult': 5,
    'Art': 2,
    'Biography': 12,
    'Business': 23,
    'History': 12,
    'Music': 0,
    'Philosophy': 38,
    'Psychology': 35,
    'Science': 2,
    'Self Help': 35
}}

Name: {name} \n
Genre Preference: {genre_pref} \n
User Question: {question} \n
User's Response: {response_text} \n

Try your best to generate nuanced, detailed, accurate predicted values. \n
If the user did not give any response to the user question, 
warn that the genre prediction may not be accurate. \n
Return a Python dictionary as the result only.
'''
    return prompt


def set_prompt():
    st.session_state.llm_prompt = generate_genre_prompt()
    st.write(st.session_state.llm_prompt)

st.button("Submit", on_click=set_prompt)