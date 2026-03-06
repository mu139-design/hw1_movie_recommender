"""
test_movie_recommender.py

Automatic test runner for movie_recommender.py
Run:
    python test_movie_recommender.py
"""

from movie_recommender import (
    load_movies,
    load_ratings,
    compute_movie_avg_ratings,
    top_n_movies,
    top_n_movies_in_genre,
    compute_genre_popularity,
    top_n_genres,
    user_top_genre,
    recommend_movies_for_user,
)


def main() -> None:
    movies_path = input("Movies file path: ").strip()
    ratings_path = input("Ratings file path: ").strip()
    user_id = input("User id to test recommendations: ").strip()

    movies_by_name_norm, genre_to_movies_norm = load_movies(movies_path)
    ratings = load_ratings(ratings_path)

    print("\n--- Loaded Counts ---")
    print("Movies:", len(movies_by_name_norm))
    print("Ratings:", len(ratings))

    movie_avgs = compute_movie_avg_ratings(ratings)

    print("\n--- Top 5 Movies Overall ---")
    print(top_n_movies(movie_avgs, movies_by_name_norm, 5))

    print("\n--- Top 5 Movies in genre 'Action' ---")
    print(top_n_movies_in_genre(movie_avgs, "Action", movies_by_name_norm, genre_to_movies_norm, 5))

    print("\n--- Top 5 Genres ---")
    gpop = compute_genre_popularity(movie_avgs, movies_by_name_norm)
    print(top_n_genres(gpop, genre_to_movies_norm, 5))

    print("\n--- User Top Genre ---")
    print(user_top_genre(ratings, movies_by_name_norm, user_id))

    print("\n--- Recommendations (3) ---")
    print(recommend_movies_for_user(ratings, movies_by_name_norm, genre_to_movies_norm, user_id, k=3))


if __name__ == "__main__":
    main()