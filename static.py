import pickle

headers_list = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0"
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15"
    },
]

with open("data/book_titles.pkl", "rb") as f:
    book_list = pickle.load(f)

with open("data/user_ids.pkl", "rb") as f:
    user_ids = pickle.load(f)


static_genre_types = {"Fiction": 0,
                      "Nonfiction": 1,
                      "Both": 2}

genres = ['Art',
 'Biography',
 'Business',
 'Chick Lit',
 "Children's",
 'Christian',
 'Classics',
 'Comics',
 'Contemporary',
 'Cookbooks',
 'Crime',
 'Ebooks',
 'Fantasy',
 'Fiction',
 'Gay and Lesbian',
 'Graphic Novels',
 'Historical Fiction',
 'History',
 'Horror',
 'Humor and Comedy',
 'Manga',
 'Memoir',
 'Music',
 'Mystery',
 'Nonfiction',
 'Paranormal',
 'Philosophy',
 'Poetry',
 'Psychology',
 'Religion',
 'Romance',
 'Science',
 'Science Fiction',
 'Self Help',
 'Suspense',
 'Spirituality',
 'Sports',
 'Thriller',
 'Travel',
 'Young Adult']

fiction_genres = [
 'Classics',
 'Contemporary',
 'Fantasy',
 'Historical Fiction',
 'Horror',
 'Mystery',
 'Romance',
 'Science Fiction',
 'Young Adult']

nonfiction_genres = [
 'Art',
 'Biography',
 'Business',
 'History',
 'Music',
 'Philosophy',
 'Psychology',
 'Science',
 'Self Help']

error_prompt_msg = "Processing error, please try again."

empty_genre_dict = {
    "Classics": 0,
    "Contemporary": 0,
    "Fantasy": 0,
    "Historical Fiction": 0,
    "Horror": 0,
    "Mystery": 0,
    "Romance": 0,
    "Science Fiction": 0,
    "Young Adult": 0,
    "Art": 0,
    "Biography": 0,
    "Business": 0,
    "History": 0,
    "Music": 0,
    "Philosophy": 0,
    "Psychology": 0,
    "Science": 0,
    "Self Help": 0
}

lex_genre_dict = {'Classics': 25, 
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
 'Self Help': 35}

suki_dict ={
"Classics":6,
"Contemporary":50,
"Fantasy":34,
"Historical Fiction":20,
"Horror":6,
"Mystery":20,
"Romance":50,
"Science Fiction":2,
"Young Adult":45,
"Art":0,
"Biography":0,
"Business":0,
"History":0,
"Music":0,
"Philosophy":0,
"Psychology":0,
"Science":0,
"Self Help":0,
}


bobby_dict = {
"Classics":1,
"Contemporary":7,
"Fantasy":4,
"Historical Fiction":6,
"Horror":0,
"Mystery":0,
"Romance":4,
"Science Fiction":3,
"Young Adult":3,
"Art":0,
"Biography":21,
"Business":28,
"History":42,
"Music":0,
"Philosophy":15,
"Psychology":24,
"Science":46,
"Self Help":13
}


beth_harmon_dict = { 
    "Classics": 20,           # She's chess-obsessed and often reads older texts
    "Contemporary": 45,       # Her internal world is very modern/emotional
    "Fantasy": 15,            # The ceiling chessboard is her personal fantasy realm
    "Historical Fiction": 30, # Set in the 60s; period themes matter
    "Horror": 10,             # Her addiction and trauma add a psychological edge
    "Mystery": 40,            # She’s enigmatic and surrounded by personal mystery
    "Romance": 25,            # Romance exists, but it’s complicated and backgrounded
    "Science Fiction": 5,     # Not a strong connection
    "Young Adult": 40,        # Coming-of-age journey with intense self-discovery
    "Art": 10,                # Chess is her art; she’s elegant and expressive
    "Biography": 35,          # She *is* a character you'd read a biography about
    "Business": 5,            # Minimal relevance, but she does think tactically
    "History": 20,            # Contextually relevant, especially Cold War tension
    "Music": 10,              # Music accompanies her internal mood
    "Philosophy": 25,         # She questions identity, purpose, genius
    "Psychology": 45,         # Huge theme: trauma, addiction, orphanhood
    "Science": 5,             # Light relevance, more analytical than scientific
    "Self Help": 10,          # There’s an underlying theme of personal growth
}


coach_carter_dict = { 
    "Classics": 10,            # He respects tradition and foundational values
    "Contemporary": 40,        # Lives in a modern world with relevant social themes
    "Fantasy": 0,              # Very grounded, real-world character
    "Historical Fiction": 2,   # Story reflects real social struggles but isn't period-based
    "Horror": 0,               # No connection
    "Mystery": 0,              # Clear and direct personality
    "Romance": 10,             # Light family/relationship themes but not central
    "Science Fiction": 0,      # Not relevant at all
    "Young Adult": 0,         # Mentoring teens is central to his character
    "Art": 6,                  # Slight appreciation—sports can be seen as artful
    "Biography": 48,           # Based on a real person; deeply inspiring life
    "Business": 37,            # Teaches responsibility, contracts, discipline—business mindset
    "History": 44,             # Connects to ongoing racial and societal history
    "Music": 8,               # Background element in culture and environment
    "Philosophy": 33,          # Strong personal code of ethics and discipline
    "Psychology": 40,          # Deeply understands and influences young minds
    "Science": 0,              # Not part of his world
    "Self Help": 45,           # Personal development and accountability are his core themes
}

profiles = {
    "Lex Fridman: Scientist": "Deeply curious... always asking the big questions in life.",
    "Suki: Avatar": "Cute and fearsome heroine from the Kyoshi island",
    "Coach Carter": "A tough but deeply nurturing mentor and father figure",
    "Bobby Axelrod: Billions": "A ruthlessly calculating Wall Street fund manager",
    "Beth Harmon: Queen's Gambit": "A chess prodigy with a brilliant but troubled mind",
    
}

# Corresponding image paths (replace with actual paths later)
profile_images = {
    "Lex Fridman: Scientist": "images/lex.png",
    "Suki: Avatar": "images/suki.png",
    "Coach Carter": "images/coach.png",
    "Bobby Axelrod: Billions": "images/bobby.png",
    "Beth Harmon: Queen's Gambit": "images/beth2.png"
}

profile_dicts ={
    "Lex Fridman: Scientist": lex_genre_dict,
    "Suki: Avatar": suki_dict,
    "Coach Carter": coach_carter_dict,
    "Bobby Axelrod: Billions": bobby_dict,
    "Beth Harmon: Queen's Gambit": beth_harmon_dict
}

empty_genre_dict = {g:0 for g in fiction_genres + nonfiction_genres}


# https://www.figma.com/design/ZVbuiFyNCDhtM2fq9sC0T1/Untitled?node-id=1001-3&p=f&t=BVHCCbNdfkEDx1vc-0


rec_df_cols = ['title',
 'author',
 'published',
 'score',
 'rating',
 'count',
 'novelty',
 'goodreads rating',
 'ratings']


neighbor_df_cols = ['user_id',
        'name', 
        'genre similarity', 
        'review samples']

questions_and_suggestions = {
    "Some of my favorite books include": "1984, The Catcher in The Rye, Dune",
    "Some of my favorite movies/tv series are": "Interstellar, Knives Out, Game of Thrones",
    # "Fictional characters I like": "Beth Harmon, James Bond",
    # "Some of my favorite video games are": "Stardew Valley, Risk of Rain, Civ 5"
}

# API info
models = ['gpt-4.1-nano', 'gpt-4o', 'gpt-4.1-mini']

prompt_instructions = """
Use the following user profile and responses to predict their book genre preferences.

Return your result as a single **JSON object** with the following two fields:

1. "predictions": A dictionary of genre scores (0–50) in this exact format:
{
    "Classics": 0,
    "Contemporary": 0,
    "Fantasy": 0,
    "Historical Fiction": 0,
    "Horror": 0,
    "Mystery": 0,
    "Romance": 0,
    "Science Fiction": 0,
    "Young Adult": 0,
    "Art": 0,
    "Biography": 0,
    "Business": 0,
    "History": 0,
    "Music": 0,
    "Philosophy": 0,
    "Psychology": 0,
    "Science": 0,
    "Self Help": 0
}

2. "explanation": 2-3 sentences (30-40 words) that explains the reasoning behind the scores in a simple, warm, and thoughtful tone. 
The explanation should be down-to-earth, penetrating, and insightful — like a friend who understands the user's taste in books.

Be specific. Provide sharp, detailed, insights that go beneath the surface or what's obvious. 
Avoid cliche pedantic or vague words phrases like 'sociopolitical' or 'thought-provoking themes'
Dig deeper into the underlying contents of the user's response instead of providing surface-level observations.

E.g. 1984 themes might include:
Totalitarianism and Absolute Power, Surveillance and Loss of Privacy, Reality Control / Manipulation of Truth
(which is much more specific than dystopian future)

DO NOT CITE RESPONSES/CONTENT THAT THE USER DID NOT INCLUDE.

Do not try to be melodramatic or poetic or emotionally over the top. Stick to intelligent but colloquial language.
Do not use overly strong words (e.g. use interest instead of love)
Avoid sounding dramatic, overly intellectual, pedantic, pretentious, or flowery.

Provide suggestions, rather than strong statements about the user's preferences.
E.g. Use "suggests", "points to", "hints at" or "you seem to enjoy" rather than "you are drawn to" or "you like"

Learn from the good examples and avoid sounding like the bad examples provided below. 
Examples:

1. Information: Genre preference = fiction, user question = some of my favorite books include, response = Dune, 1984, Catcher in the Rye, Crime and Punishment

   Great response: Your mix of favorites—Dune, 1984, Catcher in the Rye, and Crime and Punishment—suggests you’re drawn to layered stories that wrestle with power, 
   alienation, and individual agency. The combination hints at an interest in both big-picture systems 
   (like science fiction and philosophy) and internal emotional depth 
   (especially psychology and the classics). There’s also a thread of introspection and 
   critique running through these works that points to a taste for stories that dig 
   beneath the surface rather than settle for easy answers.

   Weaker response: Your favorites, from classics like Catcher in the Rye and dystopian tales like 1984, 
   hint at a keen interest in thought-provoking stories. The blend of science fiction and philosophy shines in 
   your choice of Dune and Prelude to Foundation, suggesting you enjoy narratives that explore complex societies 
   and futuristic possibilities.

   Why: The 1st response offers sharper, more specific topics such as power, alienation, individual agency.
   The 2nd response lacks the same penetrating insight. While 'complex societies, 'futuristic possibilities'
   is relevant, it is relatively vague and doesn't provide deeper insight.

2. Information: Genre preference = fiction, user question = some of my favorite books include, response = Wisdom of Insecurity, Brave New World

   Example response: "Your interest in The Wisdom of Insecurity and Brave New World suggests you enjoy books that explore the tension between 
   modern life, identity, and control — through both philosophical inquiry and imaginative futures. 
   Philosophy and psychology seem to stand out, with science fiction offering a compelling lens for abstract ideas to play out in concrete worlds."

   Why it's great: "modern life, identity, control through philosophical inquiry" is very specific and nuanced and at the same time not pedantic
   or condescending. Your tone is insightful, sharp, yet polite, amiable, and unoffensive.

3. Information: Genre preference = Both, User Question: I am in the mood for, response: a thoughtful scifi novel i can read on my flight from London to NY

    Ideal response: Since you're in the mood for a thoughtful sci-fi novel on your flight, 
    something reflective and absorbing might be a good fit—stories that invite quiet curiosity and philosophical wondering. 
    The Left Hand of Darkness by Ursula K. Le Guin could be a great pick.

    Bad response: Your interest in a thoughtful sci-fi novel for your flight hints at an appreciation for science fiction with depth and meaning. 
    The mix of thrilling speculation and philosophical context suggests intriguing narratives capturing your imagination on long journeys.

    Why: The first response understands that the user is simply asking for a suggestion based on a fleeting mood, while the second response
    mistakenly tries to project permanent beliefs or assumptions about the user.

4.  Information: Genre preference = Fiction, user question = I am in the mood for, response = The Old Man and the Sea, Dune, 1984, Brave New World, Dr Jekyll and Mr. Hyde

    Great response: Your interest in adventure and romance, paired with a relaxing mood, suggests you're in the mood for light, engaging stories with emotional warmth. 
    A mix of fantasy and young adult might suit you well.

    Bad response: Your interest in adventure and romance suggests a desire for stories that are both engaging and emotionally resonant. The mention of a relaxing read 
    for a rainy day hints at preferences for a mix of fantasy and young adult genres, where charming escapades and heartfelt moments unfold with ease.

    Why: The first response is simple, to the point, and unpretentious. The second response is melodramatic, over-the-top, and uses
    unnecessarily emotional words like "escapade" and "heartfelt moments". 


5. Information: Genre preference = Both, user question = Fictional characters I want to be like, response = Paul Atreides, James Bond
  
   Example: Wanting to be like Paul Atreides and James Bond points to an interest in characters who navigate high-stakes worlds with 
   sharp strategy, inner discipline, and a sense of control. 
   Science fiction and mystery seem to stand out, with some overlap in fantasy and philosophy where 
   ideas of power, identity, and purpose come into play.

   Why: "High-stakes worlds, sharp strategy, inner discipline" are striking accurate relevant observations.
         "Overlap" shows you are being thoughtful of other possibilities, and you back that up with
         evidence (ideas of power, identity, purpose)

If the user's response seems irrelevant/nonsensical, include a gentle note in the explanation saying the prediction may be less accurate.
If the user's response seems relevant but you don't understand it, politely say so. 

Example: "The response didn’t give much to work with, so these predictions are a bit of a guess. 
          Based on your preference in fiction, I've tailored your genres so that it leans slightly toward popular fiction genres."

Format (stick to it strictly):
{
  "predictions": { ... },
  "explanation": "..."
}

Only return valid JSON. Do not include any markdown, code formatting, or comments.
"""

dict_instructions_old = """
Genre values instructions:
- You must all allocate a total of 120 points. No more and no less. Prioritize the most directly relevant genres
- Allocate values in at least 3 different genres.
- If genre preference = fiction, allocate 0 to non-fiction genres (art, biography, business, history, philosophy, psychology, science, self-help)
- If genre preference = nonfiction, allocate 0 to fiction genres (Classics, Contemporary, Historical Fiction, Horror, Mystery, Romance, Science Fiction, young adult)

To reiterate, if Genre Preference = Fiction, ONLY allocate to (art, biography, business, history, philosophy, psychology, science, self-help). Allocate 0 points to all other genres.
If Genre Preference = Non-fiction, ONLY allocate to (Classics, Contemporary, Historical Fiction, Horror, Mystery, Romance, Science Fiction, young adult). Allocate 0 points to all other genres.
"""

dict_instructions = """
Genre values instructions:
- You must all allocate at least 150 points. 
- Allocate at least 30 points to at least 3 genres
- Allocate at least 15 points to at least 3 more genres
- Allocate at least 5 points to at least 3 more different genres.
- Capture the complexities and connections between the user's response's 

For example, Dune is primarily science fiction but also has elements of 
strategy, warfare, religion, politics etc. so allocate points to genres besides science fiction

Examples:

beth_harmon_dict = { 
    "Classics": 20,           # She's chess-obsessed and often reads older texts
    "Contemporary": 45,       # Her internal world is very modern/emotional
    "Fantasy": 15,            # The ceiling chessboard is her personal fantasy realm
    "Historical Fiction": 30, # Set in the 60s; period themes matter
    "Horror": 10,             # Her addiction and trauma add a psychological edge
    "Mystery": 40,            # She’s enigmatic and surrounded by personal mystery
    "Romance": 25,            # Romance exists, but it’s complicated and backgrounded
    "Science Fiction": 5,     # Not a strong connection
    "Young Adult": 40,        # Coming-of-age journey with intense self-discovery
    "Art": 10,                # Chess is her art; she’s elegant and expressive
    "Biography": 35,          # She *is* a character you'd read a biography about
    "Business": 5,            # Minimal relevance, but she does think tactically
    "History": 20,            # Contextually relevant, especially Cold War tension
    "Music": 10,              # Music accompanies her internal mood
    "Philosophy": 25,         # She questions identity, purpose, genius
    "Psychology": 45,         # Huge theme: trauma, addiction, orphanhood
    "Science": 5,             # Light relevance, more analytical than scientific
    "Self Help": 10,          # There’s an underlying theme of personal growth
}


coach_carter_dict = { 
    "Classics": 10,            # He respects tradition and foundational values
    "Contemporary": 40,        # Lives in a modern world with relevant social themes
    "Fantasy": 0,              # Very grounded, real-world character
    "Historical Fiction": 2,   # Story reflects real social struggles but isn't period-based
    "Horror": 0,               # No connection
    "Mystery": 0,              # Clear and direct personality
    "Romance": 10,             # Light family/relationship themes but not central
    "Science Fiction": 0,      # Not relevant at all
    "Young Adult": 0,         # Mentoring teens is central to his character
    "Art": 6,                  # Slight appreciation—sports can be seen as artful
    "Biography": 48,           # Based on a real person; deeply inspiring life
    "Business": 37,            # Teaches responsibility, contracts, discipline—business mindset
    "History": 44,             # Connects to ongoing racial and societal history
    "Music": 8,               # Background element in culture and environment
    "Philosophy": 33,          # Strong personal code of ethics and discipline
    "Psychology": 40,          # Deeply understands and influences young minds
    "Science": 0,              # Not part of his world
    "Self Help": 45,           # Personal development and accountability are his core themes
}

If the user uses vulgar language/profanities or makes inappropriate remarks (including sexist/racist/politically sensitive remarks)...
admonish the user and tell them that you will refuse to serve rude users. 

E.g. We do not tolerate the use of vulgar, abusive, or discriminatory language on this platform.
Continued misconduct may result in suspension or permanent banning of your access. Please communicate respectfully.

Do not return any genre values. That is, return 0 for all genres.
"""

def process_blurb(blurb: str, max_length: int = 400) -> str:
    if len(blurb) <= max_length:
        return blurb

    # Truncate the blurb
    snippet = blurb[:max_length]

    # Find the last occurrence of preferred punctuation
    cut_index = max(snippet.rfind(p) for p in [".", ",", "-", ";"])

    # If no punctuation found, just hard cut
    if cut_index == -1:
        return snippet.rstrip() + "..."

    return snippet[:cut_index].rstrip() + "..."

def add_padding(text: str, n: int = 6) -> str:
    nbsp = "&nbsp;" * n
    return f"{nbsp}{text}{nbsp}"



app_intro1 = """
Have you ever wandered around a bookstore, with a vague inkling of what you want but not quite sure 
where to look? Wouldn’t it be great if someone could just *magically* read your mind and suggest books
you didn’t even know you were looking for?
"""

app_intro2 = """
With Pocket Library, you can discover new books that *resonate with your unique tastes – 
sourced from reputable Goodreads users whose reading habits align with yours*. You can bet these 
suggestions are ones you can trust!  And besides…wouldn’t it be fun to know what books other 
people enjoyed that you’ve been missing out on?
"""


get_started1= """
Enter a few quick responses into the dropdown panel on the left. 
Your info will help us understand what books you might enjoy reading. 
The more examples you give, the better!
"""

get_started2= """
If you have a GoodReads account, enter your id into the left sidebar, 
and we will use your reading activity to understand your preferences
 (only if your account is public, of course).
"""

get_started3= """
If you simply want to play around, feel free to try out one of the custom-made personalities in the sidebar! 
You may find that one (or more) of these characters resonate with you!
"""

goodreads_intro = """
All data comes from GoodReads - the world's largest public website for readers and books.
"""