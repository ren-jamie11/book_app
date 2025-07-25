import streamlit as st
import pandas as pd

# Initialize session state
if "books" not in st.session_state:
    st.session_state.books = []
if "book_input" not in st.session_state:
    st.session_state.book_input = ""

# Callback to add book with LRU behavior
def add_book():
    book = st.session_state.book_input.strip()
    if book:
        # Remove if duplicate to move it to most recent
        if book in st.session_state.books:
            st.session_state.books.remove(book)
        elif len(st.session_state.books) == 3:
            st.session_state.books.pop(0)
        st.session_state.books.append(book)
        st.session_state.book_input = ""  # Clear input

# Callback to clear the list
def clear_books():
    st.session_state.books.clear()

# Input with on_change trigger
st.text_input(
    "Enter a book title",
    key="book_input",
    on_change=add_book,
    label_visibility="visible"
)

# Add a clear button
if st.button("Clear"):
    clear_books()

example_books = [
       "Harry Potter", "Meditations",
    ]

book_suggestions = st.multiselect(
    "Example answers:",
    options=example_books,
    key="book_suggestions"
)

# Display the books as a formatted string
if st.session_state.books:
    books_str = "My fav books are:\n\n"
    for i, book in enumerate(st.session_state.books, 1):
        books_str += f"{i}. {book}\n"
    st.write(books_str)
else:
    st.write("No books added yet.")
