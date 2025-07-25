import pandas as pd
import numpy as np
import streamlit as st

from static import *
from typing import List, Literal

def get_user_genre_counts(reviews):
    
    user_genre_counts = reviews.groupby('user_id')[genres].sum().T  # genres as index
    num_reviews_by_user = reviews.groupby('user_id')['title'].count()
    user_genre_pct = user_genre_counts.div(num_reviews_by_user, axis = 1)

    return user_genre_counts, user_genre_pct

def get_score(count, pct, alpha = 1):
    score = count * pct**alpha
    return score

def min_max_scale(series, max_value = 100):
    min_val = series.min()
    max_val = series.max()
    return ((series - min_val) / (max_val - min_val)) * max_value

def min_max_scale(series, max_value=100):
    if not pd.api.types.is_numeric_dtype(series):
        raise ValueError("Series must be numeric")

    non_na = series.dropna()
    if non_na.nunique() <= 1:
        return pd.Series([max_value / 2 if pd.notna(x) else np.nan for x in series], index=series.index)

    min_val = non_na.min()
    max_val = non_na.max()
    return ((series - min_val) / (max_val - min_val)) * max_value

def normalize_series(series):
    mean = series.mean()
    std = series.std()
    return (series - mean) / std

def get_url_from_user_id(user_id, users_data):
    user_row = users_data[users_data.user_id == user_id]
    if user_row:
        url = user_row['user_url'].values[0]
        return url

    return "user url not found..."


def get_top_n_reviewers(ranker, n):
    n = min(n, len(ranker))
    print("n", n)
    top_n = ranker.head(n)
    # top_n['score_normed'] = top_n['score']/np.sum(top_n['score'])
    top_n.loc[:, 'score_normed'] = top_n['score'] / np.sum(top_n['score'])

    return top_n


def get_expert_user_item_matrix(user_item_matrix, experts):
    expert_user_item_matrix =  user_item_matrix[user_item_matrix.index.isin(experts)]
    expert_user_item_matrix = expert_user_item_matrix.loc[experts]

    return expert_user_item_matrix


def get_book_scores_from_experts(user_item_matrix, rating_emphasis):
    """
    Given a user-item rating matrix with users as rows and book titles as columns,
    returns a DataFrame with the mean rating and number of ratings per book,
    ignoring zero entries.
    """

    masked = user_item_matrix.mask(user_item_matrix == 0)
    
    avg_ratings = masked.mean(axis=0)
    rating_counts = masked.count(axis=0)

    book_stats = pd.DataFrame({
        "rating": avg_ratings,
        "count": rating_counts
    })

    book_stats = book_stats.dropna(subset=["rating"])
    book_stats['score'] = get_score(book_stats['count'], book_stats['rating'], alpha = rating_emphasis)
    book_stats['score'] = min_max_scale(book_stats['score']).round(1)
    book_stats = book_stats.sort_values(by="score", ascending=False)
    book_stats = book_stats[['score', 'rating', "count"]]

    return book_stats

def format_thousands(series):
    """
    Convert integers to strings formatted in thousands with 'k' suffix.
    Examples:
        12345 -> '12.3k'
        24992 -> '25k'
        300   -> '0.3k'
    """
    return series.apply(lambda x: f"{x/1000:.1f}k".rstrip('0').rstrip('.'))

def filter_book_recs_by_score_or_n(df, n, min_score):
    high_score_books = df[df.score >= min_score]
    if len(high_score_books) >= n:
        return high_score_books.head(n)

    return high_score_books


def get_bin_labels(arr, width = 0.001):
    quantiles = np.arange(0.1, 1.0, width)
    quantile_values = np.quantile(arr, quantiles)

    bin_indices = np.digitize(arr, quantile_values, right=True)
    bin_indices = np.clip(bin_indices, 0, len(quantiles) - 1)
    bin_labels = quantiles[bin_indices].round(2)

    return bin_labels


def enrich_books_with_metadata(recommended_books, book_ratings, metadata):
    merged = recommended_books.merge(book_ratings, left_index=True, right_on='title', how='inner')
    merged = merged.set_index('title').rename(columns = {'rating_x': 'rating', 'rating_y': 'overall_rating'})
    merged_with_book_data = pd.merge(metadata, merged, left_index = True, right_index = True, how = 'right')

    return merged_with_book_data


def post_process_books(recommended_books, n):
    recommended_books = recommended_books[['author', 'publish_date', 'type','adjusted_score','rating', 'count', 'novelty', 'overall_rating', 'num_ratings']] 
    recommended_books.columns = ['author', 'published', 'type','score','rating', 'count', 'novelty', 'goodreads rating', 'ratings']
    
    recommended_books.loc[:, 'score'] = recommended_books['score'].round(1)
    recommended_books.loc[:, 'rating'] = recommended_books['rating'].round(1)
    recommended_books.loc[:, 'goodreads rating'] = recommended_books['goodreads rating'].round(1)
    recommended_books['ratings'] = format_thousands(recommended_books['ratings']).astype('object')

    return recommended_books.head(n).sort_values(by = 'score', ascending = False)

def post_process_neighbors(neighbors, users_data):
    user_cols = ['name','genre_similarity', 'read_count']

    m_neighbors = pd.merge(neighbors, users_data, left_index = True, right_on = "user_id", how = "left")
    m_neighbors['genre_similarity'] = m_neighbors['genre_similarity'].round(3) 
    m_neighbors = m_neighbors.set_index('user_id')
    m_neighbors = m_neighbors[user_cols]

    m_neighbors.columns = ['name', 'genre similarity', 'review samples']
    
    return m_neighbors


def sparse_to_df(sparse_matrix, index, columns):

    dense_df = pd.DataFrame(
        sparse_matrix.toarray(), 
        index=index,
        columns=columns
    )

    return dense_df

def get_expert_user_item_sparse(user_item_sparse, user_ids, experts):
    """
    Args:
        user_item_sparse: csr_matrix, full user-item matrix
        user_ids: list of user IDs (row index order of the sparse matrix)
        experts: list or pd.Index of expert user IDs

    Returns:
        csr_matrix with only expert users
    """
    user_id_to_row = {uid: i for i, uid in enumerate(user_ids)}
    expert_indices = [user_id_to_row[uid] for uid in experts if uid in user_id_to_row]
    return user_item_sparse[expert_indices, :]


def format_rating_count(book_stats, rating_emphasis):
    book_stats = book_stats.dropna(subset=["rating"])
    book_stats['score'] = get_score(book_stats['count'], book_stats['rating'], alpha = rating_emphasis)
    book_stats['score'] = min_max_scale(book_stats['score']).round(1)
    book_stats = book_stats.sort_values(by="score", ascending=False)
    book_stats = book_stats[['score', 'rating', "count"]]

    return book_stats

def get_book_scores_from_experts_sparse(user_item_sparse, book_index):
    """
    Vectorized version: takes a CSR sparse matrix and computes per-item:
    - mean rating (ignoring zeros)
    - count of non-zero ratings
    Returns a DataFrame with 'rating' and 'count' columns.
    """

    # Convert to CSC for efficient column operations
    user_item_csc = user_item_sparse.tocsc()

    # Count of non-zero ratings per column (i.e. per book)
    rating_counts = np.diff(user_item_csc.indptr)

    # Sum of all non-zero ratings per column
    rating_sums = np.asarray(user_item_csc.sum(axis=0)).ravel()

    # Avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        avg_ratings = np.true_divide(rating_sums, rating_counts)
        avg_ratings[np.isnan(avg_ratings)] = 0.0  # for columns with 0 ratings

    return pd.DataFrame({
        "rating": avg_ratings,
        "count": rating_counts
    }, index = book_index)

def filter_books_by_type(df, book_type):
    return df[df.type == book_type]

def get_recommendation_from_top(ranker, novelty_factor, rating_emphasis, sparse_user_item_matrix,
                                users_data, book_ratings, metadata, book_type: Literal["Fiction", "Nonfiction", "Both"],
                                num_reviewers = 100, min_similarity = 0.8):
    
    if book_type not in {"Fiction", "Nonfiction", "Both"}:
        raise ValueError(f"Invalid genre: {book_type}")

    top_n = get_top_n_reviewers(ranker, num_reviewers)
    top_n = top_n[top_n.genre_similarity >= min_similarity]
    experts = top_n.index
    neighbors = post_process_neighbors(top_n.head(num_reviewers), users_data = users_data)
    
    """ New Implementation"""
    expert_user_item_matrix_sparse = get_expert_user_item_sparse(sparse_user_item_matrix, user_ids, experts)
    expert_ratings = get_book_scores_from_experts_sparse(expert_user_item_matrix_sparse, book_index = book_list)
    expert_ratings = format_rating_count(expert_ratings, rating_emphasis = rating_emphasis)


    rec_books_with_metadata = enrich_books_with_metadata(expert_ratings, book_ratings, metadata)
    rec_books_with_metadata['novelty'] = get_bin_labels(rec_books_with_metadata.num_ratings.values)
    rec_books_with_metadata['novelty'] = np.abs(1 - rec_books_with_metadata['novelty'])
    rec_books_with_metadata['adjusted_score'] = get_score(count = rec_books_with_metadata['score'],
                                                          pct = rec_books_with_metadata['novelty'],
                                                          alpha = novelty_factor)
    
    rec_books_with_metadata['adjusted_score'] = min_max_scale(rec_books_with_metadata['adjusted_score'])
    
    # filter by fiction vs nonfiction or both!
    book_type = book_type.lower()
    if book_type == 'fiction' or book_type == 'nonfiction':
        rec_books_with_metadata = rec_books_with_metadata[rec_books_with_metadata.type == book_type]

    best_books = post_process_books(rec_books_with_metadata, n = 50)

    
    return best_books, neighbors


def label_reviews_with_genre(all_reviews, genre_labels):
    all_labeled_reviews = all_reviews.merge(
        genre_labels, 
        on='title', 
        how='inner'
    )

    all_labeled_reviews = all_labeled_reviews.drop_duplicates(subset=['title', 'user_id', 'rating'])
    return all_labeled_reviews

@st.cache_data
def get_user_genre_counts_and_pcts(user_reviews, genre_labels, max_value = None):
    if len(user_reviews) == 0:
        return pd.DataFrame(), pd.DataFrame()

    this_user_reviews_labeled = label_reviews_with_genre(user_reviews, genre_labels)
    this_user_genre_counts, this_user_genre_pct = get_user_genre_counts(this_user_reviews_labeled)

    if max_value:
        this_user_genre_pct[this_user_genre_pct.columns[0]] = this_user_genre_pct[this_user_genre_pct.columns[0]].clip(upper = max_value)

    return this_user_genre_counts, this_user_genre_pct

def cosine_similarity_manual(A, B):
    A_norm = A / np.linalg.norm(A, axis=1, keepdims=True)
    B_norm = B / np.linalg.norm(B, axis=1, keepdims=True)
    return np.dot(A_norm, B_norm.T)

def get_user_similarities_ranker_by_genre(this_user_genre_pct, user_genre_counts, other_users_genre_pct, alpha, min_similarity):    
    # construct matrix
    M = other_users_genre_pct.values
    v = this_user_genre_pct.values
    similarities = cosine_similarity_manual(M.T, v.T).ravel()
    other_users = other_users_genre_pct.T.index
    similarity_ranker = pd.DataFrame({'other_users': other_users, 'genre_similarity': similarities})
    
    """ Can improve this!!!  """
    # Formatting the similarity table
    similarity_ranker = similarity_ranker.set_index("other_users")
    similarity_ranker['read_count'] = user_genre_counts.sum(axis = 0)  # IMPROVE THISSSSS
    similarity_ranker = similarity_ranker[similarity_ranker.genre_similarity >= min_similarity]
    similarity_ranker['score'] = get_score(similarity_ranker['read_count'], similarity_ranker['genre_similarity'], alpha = alpha)
    similarity_ranker = similarity_ranker.sort_values(by = 'score', ascending = False) 
    
    return similarity_ranker


""" USE THIS FOR CUSTOME GENRE PCT"""
def recommend_books_by_custom_genre_pct(book_type, custom_user_genre_pct, novelty_factor, rating_emphasis,
                                        user_genre_counts, other_users_genre_pct,
                                        sparse_user_item_matrix, users_data, book_ratings,
                                        metadata, hide_read, user_reviews = None):

    genre_similarity_ranker = get_user_similarities_ranker_by_genre(custom_user_genre_pct, user_genre_counts, other_users_genre_pct,
                                                                    alpha = 250, min_similarity = 0.8)
    
    recommended_books, neighbors = get_recommendation_from_top(genre_similarity_ranker, novelty_factor, rating_emphasis, sparse_user_item_matrix,
                                                               users_data, book_ratings, metadata, book_type)
    
    """ (add a toggle maybe!!! up to them)"""
    if hide_read:
        if len(user_reviews) > 0:
            recommended_books = recommended_books[~recommended_books.index.isin(user_reviews.title.values)]
    
    return recommended_books, neighbors

def adjust_genre_values(df: pd.DataFrame, genre_list: List[str], values: List[float]) -> pd.DataFrame:

    if df.shape[1] != 1:
        raise ValueError(f"DataFrame must have exactly one column (df length is {len(df)}).")
        
    if len(genre_list) != len(values):
        raise ValueError("genre_list and values must have the same length.")

    column_name = df.columns[0]

    for genre, value in zip(genre_list, values):
        if genre in df.index:
            df.loc[genre, column_name] = value
        else:
            print(f"Warning: Genre '{genre}' not found in the DataFrame index. Skipping.")

    return df

def retrieve_genre_values_from_df(df, genre_list):
    if len(df) == 0:
        return empty_genre_dict

    genre_values = df[df.index.isin(genre_list)].values.flatten()

    if len(genre_values) != len(genre_list):
        raise ValueError("Not all genres were in genre df")
    
    res_dict = {g:int(v*100) for g,v in zip(genre_list, genre_values)}
    return res_dict