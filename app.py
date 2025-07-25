import streamlit as st
import time
import json

from openai import OpenAI

from static import *
from get_user_reviews import *
from main_genre_book_recommender_sparse import *
from user_review_cache_class import UserActivityCache
from scipy.sparse import load_npz

import logging
logging.basicConfig(filename='myProgramLog.txt', level=logging.DEBUG,
format=' %(asctime)s -  %(levelname)s -  %(message)s')

# Idea: Generate AI description for goodreads users.
# Long term: Use AI prompt for RAG/embedding with blurb.

# Rate limiting: https://blog.schogini.com/html_files/how-to-rate-limit-streamlit.html
@st.cache_resource
def get_openai_client(api_key):
    if "openai_client" not in st.session_state:
        st.session_state.openai_client = OpenAI(api_key=api_key)
    return st.session_state.openai_client   

client = get_openai_client(st.secrets["OpenAI_key"])

st.set_page_config(page_title="Pocket Library", layout="wide")
left_column, breaker, col_recommend = st.columns([4.5, 0.5, 6])

def white_space(n):
    for _ in range(n):
        st.write("")
    return
                
def reset_sliders(default=0):
    for g in fiction_genres:
        st.session_state[g] = default
    for g in nonfiction_genres:
        st.session_state[g] = default
    return

# Personality Quiz Stuff

if "response_dict" not in st.session_state:
    st.session_state.response_dict = {q: [] for q in questions_and_suggestions.keys()}

if "responses" not in st.session_state:
    st.session_state.responses = []
if "response_input" not in st.session_state:
    st.session_state.response_input = ""
if "llm_prompt" not in st.session_state:
    st.session_state.llm_prompt = ""

if "question_suggestion" not in st.session_state:
    st.session_state.question_suggestion = list(questions_and_suggestions.keys())[0]

# Slider values are from 0 to max_genre_pct
max_genre_pct = 50

def set_sliders(genre_values_dict: dict):
    """
    Set slider values (provided by dict)
    """
    for k,v in genre_values_dict.items():
        st.session_state[k] = min(v, max_genre_pct)
    return

def check_if_sliders_zero():
    for g in fiction_genres + nonfiction_genres:
        if st.session_state[g] != 0:
            return False
    return True

if "too_few_responses" not in st.session_state:
    st.session_state.too_few_responses = False

if "too_many_responses" not in st.session_state:
    st.session_state.too_many_responses = False

if "response_too_long" not in st.session_state:
    st.session_state.response_too_long = False

MIN_RESPONSES = 3
MAX_RESPONSES = 10
MAX_RESPONSE_LENGTH = 40
def add_response(max_response_length = MAX_RESPONSE_LENGTH, max_responses = MAX_RESPONSES):
    response = st.session_state.response_input.strip()
    response_list = st.session_state.response_dict[st.session_state.question_suggestion]

    if response:
        if response in response_list:
            st.session_state.response_input = ""  
            st.session_state.response_too_long = False
        elif len(response_list) < max_responses:
            if len(response) <= max_response_length:
                # success
                response_list.append(response)
                st.session_state.response_input = ""  
                st.session_state.response_too_long = False
            else:
                st.session_state.response_too_long = True
        else:
            st.session_state.response_too_long = False
            st.session_state.too_many_responses = True

def clear_responses():
    st.session_state.too_many_responses = False
    response_list = st.session_state.response_dict[st.session_state.question_suggestion]
    response_list.clear()

def remove_last_response():
    st.session_state.too_many_responses = False
    response_list = st.session_state.response_dict[st.session_state.question_suggestion]
    if response_list:
        response_list.pop()

def generate_genre_prompt():
    name = st.session_state.get("name", "").strip() or "Unknown"
    genre_pref = st.session_state.get("reading_preference", "Unknown")
    if genre_pref == "Both":
        genre_pref = "Both fiction and non-fiction"

    question = st.session_state.get("question_suggestion", "N/A")
    responses = []
    if question in st.session_state.response_dict:
        responses = st.session_state.response_dict[question]

    # verify length
    if len(responses) < MIN_RESPONSES:
        st.session_state.too_few_responses = True
    else:
        st.session_state.too_few_responses = False

    # user's response
    response_text = ", ".join(responses) if responses else "No responses given"

    prompt = f'''
    Name: {name} \n
    Genre Preference: {genre_pref} \n
    User Question: {question} \n
    User's Response: {response_text} \n
    '''
    return prompt


def call_openai_api(survey_response, instructions, dict_instructions, client, model = 'gpt-4o'):
    
    prompt = instructions + survey_response + dict_instructions
    
    start = time.time()

    try:
        response = client.chat.completions.create(
            model=model, 
            messages=[
                {"role": "system", "content": "You are an AI assistant designed to output only JSON objects."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} 
        )

    except Exception as e:
        raise Exception(f"Error while calling API: {e}")

    end = time.time()
    elapsed = end - start

    logging.info(f"Prompt\n{survey_response}")
    logging.info(f'Time needed to call API: {elapsed:.2f} seconds \n')

    return response 

def parse_llm_output(response):
    # get response (JSON)
    json_output = response.choices[0].message.content

    # turn to python dict
    dict_output = json.loads(json_output)

    # return final outputs (genre dict + blurb)
    genre_preds_dict = dict_output["predictions"]
    genre_preds_blurb = dict_output.get('explanation', 'No explanation provided.')

    logging.info(genre_preds_dict)
    logging.info(genre_preds_blurb)

    return genre_preds_dict, genre_preds_blurb

@st.cache_data
def survey_results(survey_response, instructions = prompt_instructions, dict_instructions = dict_instructions,
                   client = client, model = 'gpt-4o'):

    try:
        response = call_openai_api(survey_response, instructions, dict_instructions, client, model)
    except Exception as e:
        st.write("An error has occurred with the survey...sorry about that")
    
    genre_preds_dict, genre_preds_blurb = parse_llm_output(response)

    return genre_preds_dict, genre_preds_blurb

if "survey_genre_dict" not in st.session_state:
    st.session_state.survey_genre_dict = dict()
if "survey_genre_blurb" not in st.session_state:
    st.session_state.survey_genre_blurb = ""
if "update_sliders_via_survey" not in st.session_state:
    st.session_state.update_sliders_via_survey = False

# RATE LIMIT
if "last_submit_time" not in st.session_state:
    st.session_state.last_submit_time = 0

if "prompt_cache" not in st.session_state:
    st.session_state.prompt_cache = UserActivityCache(maxsize=10)

def submit_personality_form(cooldown = 30):
    now = time.time()
    prompt = generate_genre_prompt()

    if st.session_state.too_few_responses:
        return
    
    # check if we need to rate limit (new survey response)
    is_repeat = st.session_state.prompt_cache.get(prompt) is not None
    last_submit_time = st.session_state.get("last_submit_time", 0)
    if not is_repeat and now - last_submit_time < cooldown:
        remaining = int(cooldown - (now - last_submit_time))
        st.warning(f"Please wait {remaining} more seconds before submitting again.")
        return
    
    # enough time passed or we already seen this response
    st.session_state.survey_genre_preds_dict, st.session_state.survey_genre_blurb = survey_results(prompt)
    set_sliders(st.session_state.survey_genre_preds_dict)

    # only update time if it's a new survey response
    if not is_repeat:
        st.session_state.last_submit_time = now

    st.session_state.prompt_cache.set(prompt, now)

    # RESET RECOMMENDATIONS
    st.session_state.recommendations = pd.DataFrame(columns=rec_df_cols)
    
def reset_everything():
    reset_sliders()
    st.session_state.survey_genre_blurb = ""
    st.session_state.recommendations = pd.DataFrame(columns=rec_df_cols)


with left_column:
    st.write("")
    st.subheader("📚 Your profile")
    
    st.write("")
    st.write("")
    with st.expander("Get started"):
        
        name_col, gender_col = st.columns([3,3])
        with name_col:
            name = st.text_input("Name:", key="name")

        with gender_col:
            reading_preference = st.radio(
                "I tend to read:",
                options=static_genre_types.keys(),
                index = 2,
                horizontal=True,
                key="reading_preference"
            )

        god_col1, god_col2 = st.columns([3,3])
        
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

            survey_button = st.button(label = "Submit", 
                                      on_click=submit_personality_form)

        with god_col2:
            specific_suggestion = questions_and_suggestions[st.session_state["question_suggestion"]]

            response_input = st.text_input(
                f"Examples: {specific_suggestion}", 
                key="response_input",
                on_change=add_response,
                label_visibility="visible"
            )

            undo_col, clear_col = st.columns([1.5, 5])
            with undo_col:
                if curr_responses:
                    st.button("Undo", on_click=remove_last_response)
            with clear_col:
                if curr_responses:
                    st.button("Clear", on_click=clear_responses)
            
            if st.session_state.too_few_responses:
                st.write(f"Please enter at least {MIN_RESPONSES} responses.")

            if st.session_state.too_many_responses:
                st.write(f"You may only enter up to {MAX_RESPONSES} responses.")

            if st.session_state.response_too_long:
                st.write(f"Please keep your response under {MAX_RESPONSE_LENGTH} characters")

    # st.write(st.session_state.llm_prompt)
    st.write(st.session_state.survey_genre_blurb)

    fiction_sliders, col2, nonfiction_sliders = st.columns([2,0.5,2])


# ------ Load parquet files! --------
file_paths = ["data/all_books_final.parquet",
              "data/users_data.parquet",
              "data/genre_labels.parquet",
              "data/all_labeled_reviews.parquet",
              "data/compact_user_genre_pct.parquet"]

@st.cache_data
def read_parquet(file_path):
    df = pd.read_parquet(file_path)
    return df

all_books = read_parquet("data/all_books_fully_enriched.parquet")
all_books_ratings = all_books[['title', 'rating', 'num_ratings']]
books_author_date = all_books[['title', 'author', 'publish_date', 'type']]
books_author_date = books_author_date.set_index('title')
books_covers = all_books[['title', 'author', 'blurb', 'image_url', 'book_url']].set_index('title')

# book_cover_info = all_books[['title', 'author', 'book_url', 'blurb', 'image_url']] 

users_data = read_parquet("data/users_data.parquet")
genre_labels = read_parquet("data/genre_labels.parquet")
all_labeled_reviews = read_parquet("data/all_labeled_reviews.parquet")
compact_user_genre_pct = read_parquet("data/compact_user_genre_pct.parquet")
# ------ Finished loading parquet files --------

st.sidebar.write("")
st.sidebar.title("🔍 Load Reviews")
user_id = st.sidebar.text_input("GoodReads User ID", key = 'user_id_chatbox')

def genre_subtext(title, spaces = 2):
    """ Basic formatting/text function
        (not important)
    """
    for _ in range(spaces):
        st.write("")
    st.write(f"**{title}**")

with fiction_sliders:

    st.button(
        "Reset",
        on_click=reset_everything,
        key="reset_sliders"
    )
    
    genre_subtext("Fiction", spaces = 1)

    # Fiction 
    classics = st.slider("Classics", 0, max_genre_pct, key="Classics")
    contemporary = st.slider("Contemporary", 0, max_genre_pct, key="Contemporary")
    fantasy = st.slider("Fantasy", 0, max_genre_pct, key="Fantasy")
    historical_fiction = st.slider("Historical fiction", 0, max_genre_pct, key="Historical Fiction")
    horror = st.slider("Horror", 0, max_genre_pct, key="Horror")
    mystery = st.slider("Mystery", 0, max_genre_pct, key="Mystery")
    romance = st.slider("Romance", 0, max_genre_pct, key="Romance")
    science_fiction = st.slider("Science fiction", 0, max_genre_pct, key="Science Fiction")
    young_adult = st.slider("Young adult", 0, max_genre_pct, key="Young Adult")

with nonfiction_sliders:
    # st.subheader("")
    genre_subtext("Nonfiction", spaces = 5)

    # Nonfiction 
    art = st.slider("Art", 0, max_genre_pct, key="Art")
    biography = st.slider("Biography", 0, max_genre_pct, key="Biography")
    business = st.slider("Business", 0, max_genre_pct, key="Business")
    history = st.slider("History", 0, max_genre_pct, key="History")
    music = st.slider("Music", 0, max_genre_pct, key="Music")
    philosophy = st.slider("Philosophy", 0, max_genre_pct, key="Philosophy")
    psychology = st.slider("Psychology", 0, max_genre_pct, key="Psychology")
    science = st.slider("Science", 0, max_genre_pct, key="Science")
    self_help = st.slider("Self help", 0, max_genre_pct, key="Self Help")

fiction_values = [st.session_state[g]/100 for g in fiction_genres]
nonfiction_values = [st.session_state[g]/100 for g in nonfiction_genres]

def load_user_reviews_button(genre_labels: pd.DataFrame, 
                             fiction_genres: List[str], nonfiction_genres: List[str]):
    """
    - Loads user reviews from GoodReads website
    - Extracts 18 genre info from user
    - Set slider values to extracted values
    - Ready to be used in recommender engine

    Args:
        - user_id: The user's id
        - genre_labels: Enriches books with correct genre labels
        - fiction_genres: List[str] of fiction genres
        - nonfiction_genres: List[str] of nonfiction genres
    """
    st.session_state.sidebar_acknowledged = True
    # get what's in the chatbox
    user_id_entry = st.session_state['user_id_chatbox']
    if user_id_entry.strip() == "":
            st.error("Please enter a valid user ID.")
    else:
        # refresh recs and neighbors (before user presses 'recommend' button)
        st.session_state.recommendations = pd.DataFrame(columns=rec_df_cols)
        st.session_state.neighbors = pd.DataFrame(columns = neighbor_df_cols)

        with st.spinner("Loading user reviews..."):
            st.session_state.user_reviews = get_user_reviews_from_cache(user_id_entry)
        
        # get genre info from user's reviews
        temp_genre_counts, temp_genre_pcts = get_user_genre_counts_and_pcts(st.session_state.user_reviews, 
                                                                            genre_labels, max_value= max_genre_pct/100)

        # check if loaded successfully
        if len(temp_genre_pcts) > 0:
            st.session_state.load_user_status = True
        else:
            st.session_state.load_user_status = False

        # set sliders to user's genre values
        user_fiction_values_dict = retrieve_genre_values_from_df(temp_genre_pcts, fiction_genres)
        user_nonfiction_values_dict = retrieve_genre_values_from_df(temp_genre_pcts, nonfiction_genres)

        set_sliders(user_fiction_values_dict)
        set_sliders(user_nonfiction_values_dict)

@st.cache_data
def load_sparse_user_item_matrix(filepath = "data/user_item_sparse.npz"):
    loaded_sparse = load_npz(filepath)
    return loaded_sparse

# Sparse user item matrix
sparse_user_item_matrix = load_sparse_user_item_matrix()

with col_recommend:

    # --- Persist cache between reruns ---
    if "cache" not in st.session_state:
        st.session_state.cache = UserActivityCache(maxsize=5)

    cache = st.session_state.cache
    
    def get_user_reviews_from_cache(user_id):
        """
        Load user's review data from GoodReads url
        Stores in cache (for easier repeat retrieval)
        """
        cached = cache.get(user_id)
        if cached is not None:
            return cached
        
        user_reviews_dicts = get_reviews_from_user_url(user_id)
        user_reviews = pd.DataFrame(user_reviews_dicts)
        cache.set(user_id, user_reviews)
        return user_reviews

    # Takes up a lot of RAM!!
    if "user_genre_counts" not in st.session_state:
        st.session_state.user_genre_counts, st.session_state.user_genre_pct = get_user_genre_counts(all_labeled_reviews)

    user_genre_counts, user_genre_pct = st.session_state.user_genre_counts, st.session_state.user_genre_pct

    if 'user_reviews' not in st.session_state:
        st.session_state.user_reviews = pd.DataFrame()

    # Genre info (what recommender uses as primary input)
    if "user_genre_stats_main" not in st.session_state:
        st.session_state.this_user_genre_counts, st.session_state.user_genre_stats_main = pd.DataFrame, pd.read_parquet("data/default_genre_when_no_load.parquet")

    if "neighbors" not in st.session_state:
        st.session_state.neighbors = pd.DataFrame()

    load_user_kwargs = {
        "genre_labels": genre_labels,
        "fiction_genres": fiction_genres, 
        "nonfiction_genres": nonfiction_genres
    }

    load_button = st.sidebar.button("Load", on_click = load_user_reviews_button, kwargs = load_user_kwargs)

    st.sidebar.caption("""Use id from your ratings page (e.g. 155041466)
                       www.goodreads.com/review/list/155041466?""")

    if "load_user_status" not in st.session_state:
        st.session_state.load_user_status = True

    if not st.session_state.load_user_status:
        # Restore to default values if can't load user data
        st.session_state.this_user_genre_counts, st.session_state.user_genre_stats_main = pd.DataFrame, pd.read_parquet("data/default_genre_when_no_load.parquet")
        st.sidebar.warning("Could not retrieve this user's data")

    st.sidebar.divider()
    st.sidebar.subheader("Reader personality")
    st.sidebar.caption(
        "If you don't have a GoodReads ID, feel free to toggle the sliders "
        "or try out these personalities!"
    )

    selected_profile = st.sidebar.selectbox(
    "Choose a reader personality",
    list(profiles.keys())
)

    # Personality choices
    persons, captions = st.sidebar.columns([1,2])

    with persons:
        st.image(profile_images[selected_profile], width=100)

    with captions:
        st.write(f"**{selected_profile}**")
        st.caption(profiles[selected_profile])

    # See static.py for preloaded personality dicts
    load_person_button = st.sidebar.button(
            label="Try me",
            on_click=set_sliders, 
            kwargs={"genre_values_dict": profile_dicts[selected_profile]}
        )
    
    if load_person_button:
        st.session_state.recommendations = pd.DataFrame(columns=rec_df_cols)

    st.sidebar.divider()

    st.title("📚 Your books")
    st.write("")

    with st.expander("About this app"):
        expander_dimensions = [2.5, 0.2, 1]
        about_tab, how_tab = st.tabs(["Intro", "How to use"])

        with about_tab: 
            word_col, space_col, book_image_col = st.columns(expander_dimensions) 
            
            with word_col:
                st.write("")
                st.write("#### Pocket Library: the new way to discover books")
                # st.write("*The new way to discover books)
                st.write(app_intro1)
                st.write("*Tell me more!*")
                st.write(app_intro2)
                
            with book_image_col:
                st.write("")
                st.image("images/book_app_logo.png", width=200)

        with how_tab: 
            word_col, space_col, book_image_col = st.columns(expander_dimensions) 
            
            with word_col:
                st.write("")
                st.write('**Getting started**')
                # st.write("*The new way to discover books)
                st.write(get_started1)
                st.write("*What if I have a GoodReads account?*")
                st.write(get_started2)
                st.write("*Cool! Anything else?*")
                st.write(get_started3)

            with book_image_col:
                st.write("")
                st.image("images/book_app_logo.png", width=200)

    st.write("")
    st.write("**Recommendations**")
    mode = st.selectbox("Mode", ["Classic", "Surprise Me"])
    container1, container2, container3 = st.columns([3, 4, 2])
    with container1:
        recommend_button = st.button("Get recommendations")

    with container2:
        genre_filter_preference = st.radio(
                "genre",
                options=static_genre_types.keys(),
                index = static_genre_types[st.session_state.reading_preference],
                horizontal=True,
                key="genre_filter_preference",
                label_visibility="collapsed",
            )

    with container3:
        hide_read = st.checkbox("Hide Books Already Read", value=True, key="hide_read")

    # def acknowledge_sidebar():
    #     st.session_state.sidebar_acknowledged = True

    # if "sidebar_acknowledged" not in st.session_state:
    #     st.session_state.sidebar_acknowledged = False

    # if not st.session_state.sidebar_acknowledged:
    #     st.write("")
    #     st.write("")
    #     st.markdown(
    #         '<span style="color: navy; font-weight: bold;">'
    #         'Toggle sliders to get recs, '
    #         'or open sidebar (top left) to try out personalities!'
    #         '</span>',
    #         unsafe_allow_html=True
    #     )

    #     st.markdown('<span style="color: navy;">Zoom out (ctrl + "-") to 75% for best experience </span>', 
    #                 unsafe_allow_html=True)
    #     st.button("Got it!", on_click=acknowledge_sidebar)
        
    # Mapping from mode name to novelty factor
    mode_to_novelty = {
        "Classic": 0.1,
        "Surprise Me": 1
    }
    novelty_factor = mode_to_novelty[mode]

    st.write("")

    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = pd.DataFrame(columns=rec_df_cols)

    if recommend_button:
        # Maps slider values to genre vector
        st.session_state.user_genre_stats_main = adjust_genre_values(st.session_state.user_genre_stats_main,
                                                                        fiction_genres + nonfiction_genres,
                                                                        fiction_values + nonfiction_values
                                                                        )
 
        # Gets recommendations!!
        st.session_state.recommendations, st.session_state.neighbors = recommend_books_by_custom_genre_pct(st.session_state.genre_filter_preference,
                                                                st.session_state.user_genre_stats_main, novelty_factor = novelty_factor,
                                                                rating_emphasis = 8, user_reviews = st.session_state.user_reviews,
                                                                user_genre_counts = user_genre_counts, other_users_genre_pct = compact_user_genre_pct,
                                                                sparse_user_item_matrix = sparse_user_item_matrix, users_data = users_data, 
                                                                book_ratings = all_books_ratings, metadata = books_author_date, hide_read=st.session_state.hide_read)

        # st.write(st.session_state.recommendations.columns)

    # Display
    if len(st.session_state.recommendations) > 0:
        result= st.session_state.recommendations.head(10)
        st.dataframe(result, height = 210)

        # display book covers!
        recommended_book_covers = books_covers.loc[result.index]
        recommended_book_covers_dict = recommended_book_covers.to_dict(orient='index')
        
        white_space(2)
        tabs = st.tabs([add_padding(i+1, 10) for i in range(len(recommended_book_covers_dict))])

        for tab, (title, info) in zip(tabs, recommended_book_covers_dict.items()):
            with tab:
                image_col, space_col, content_col = st.columns([1, 0.1, 4])  

                with image_col:
                    st.write("")
                    st.image(info.get("image_url", "image unavailable"), width = 180)

                with content_col:
                    st.subheader(title)
                    st.markdown(f"*{info.get('author', '')}*") 
                    st.write("")
                    
                    blurb = info.get("blurb", "blurb unavailable")
                    blurb = process_blurb(blurb)
                    st.write(blurb)
                    
                    book_url = info.get("book_url", "#")
                    st.markdown(f"[Read more]({book_url})")


        if check_if_sliders_zero():
            st.warning("Kind reminder to toggle genres before loading recommendations")


    else:
        st.session_state.recommendations = pd.DataFrame(columns=rec_df_cols)
        st.dataframe(st.session_state.recommendations, height = 210)


with left_column:
    st.divider()
    st.write(""" **Relevant**: Recs come from those whose reading profiles are just like yours""")
    st.write(""" **Reliable**: Recs are based on the behavior of highly active and informed readers""")
    st.write(""" **Transparent**: You know exactly who/where your recommendations are coming from""") 

    # st.divider()
    # st.write("**Technical details**")
    st.write("")
    data_tab, glossary_tab, neighbor_tab = st.tabs(["Data", "Glossary", "Neighbor users"])

    with data_tab:
        data_col1, _, data_col2 = st.columns([2,.5,3])
        with data_col1:
            st.write("**Coverage**")
            st.write("- 16,000+ books")
            st.write("- 9,500+ user profiles")
            st.write("- 475,000+ ratings")
        with data_col2:
            st.write("**Source**")
            st.write(goodreads_intro)
            st.write("")
            st.markdown("[GoodReads](https://www.goodreads.com/)")
    with glossary_tab:
        st.write("*Definitions*")
        st.caption("- 'rating': Average rating given by neighbor users (more relevant/reliable than all users)")
        st.caption("- 'count': represents how many neighbor users have rated the book (out of 100)")
        st.caption("- 'novelty': Inversely related to number of people who have read this book")
    with neighbor_tab:
        st.write("**Neighbor users**")
        st.caption(""" Recommendations are based on books highly rated by top 100 reputable GoodReads users 
                        whose reading patterns most closely match your genres above.""")
        st.dataframe(st.session_state.neighbors, height = 210)