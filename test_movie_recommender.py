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

MOVIES_PATH = "movies.txt"
RATINGS_PATH = "ratings.txt"
TEST_USER_ID = "6"
EPSILON = 1e-6

tests_run = 0
tests_passed = 0


def check_equal(test_name: str, actual, expected) -> None:
    """Check whether actual == expected and print PASS/FAIL."""
    global tests_run, tests_passed
    tests_run += 1

    if actual == expected:
        tests_passed += 1
        print(f"[PASS] {test_name}")
    else:
        print(f"[FAIL] {test_name}")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")


def check_float(test_name: str, actual: float, expected: float) -> None:
    """Check whether two floats are approximately equal."""
    global tests_run, tests_passed
    tests_run += 1

    if abs(actual - expected) < EPSILON:
        tests_passed += 1
        print(f"[PASS] {test_name}")
    else:
        print(f"[FAIL] {test_name}")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")


def check_dict_floats(test_name: str, actual: dict, expected: dict) -> None:
    """Check dictionaries whose values are floats."""
    global tests_run, tests_passed
    tests_run += 1

    if set(actual.keys()) != set(expected.keys()):
        print(f"[FAIL] {test_name}")
        print(f"  Expected keys: {set(expected.keys())}")
        print(f"  Actual keys:   {set(actual.keys())}")
        return

    for key in expected:
        if abs(actual[key] - expected[key]) >= EPSILON:
            print(f"[FAIL] {test_name}")
            print(f"  Key:      {key}")
            print(f"  Expected: {expected[key]}")
            print(f"  Actual:   {actual[key]}")
            return

    tests_passed += 1
    print(f"[PASS] {test_name}")


def check_string_case_insensitive(test_name: str, actual: str, expected: str) -> None:
    """Check strings ignoring case and surrounding spaces."""
    global tests_run, tests_passed
    tests_run += 1

    if actual.strip().lower() == expected.strip().lower():
        tests_passed += 1
        print(f"[PASS] {test_name}")
    else:
        print(f"[FAIL] {test_name}")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")


def main() -> None:
    """Run all automatic tests."""

    # --------------------------------------------------
    # Load data
    # --------------------------------------------------
    movies_by_name_norm, genre_to_movies_norm = load_movies(MOVIES_PATH)
    ratings = load_ratings(RATINGS_PATH)

    # --------------------------------------------------
    # Basic load tests
    # --------------------------------------------------
    check_equal("load_movies movie count", len(movies_by_name_norm), 9)
    check_equal("load_movies genre count", len(genre_to_movies_norm), 3)
    check_equal("load_ratings count", len(ratings), 54)

    # --------------------------------------------------
    # Expected values
    # These keys are normalized because your program uses
    # normalized movie names internally.
    # --------------------------------------------------
    expected_movie_avgs = {
        "toy story (1995)": 3.8333333333333335,
        "jumanji (1995)": 3.4166666666666665,
        "tom and huck (1995)": 2.8333333333333335,
        "grumpier old men (1995)": 4.0,
        "waiting to exhale (1995)": 2.5,
        "father of the bride part ii (1995)": 4.0,
        "heat (1995)": 4.25,
        "sudden death (1995)": 3.3333333333333335,
        "goldeneye (1995)": 3.0,
    }

    expected_genre_popularity = {
        "adventure": 3.361111111111111,
        "comedy": 3.5,
        "action": 3.5277777777777777,
    }

    # These expected outputs assume the finished functions return
    # lists of tuples in the form:
    # (movie_name, average_rating)
    # and
    # (genre_name, popularity_score)

    expected_top_5_movies = [
    ("Heat (1995)", 4.25),
    ("Father of the Bride Part II (1995)", 4.0),
    ("Grumpier Old Men (1995)", 4.0),
    ("Toy Story (1995)", 3.8333333333333335),
    ("Jumanji (1995)", 3.4166666666666665),
    ]

    expected_top_action = [
        ("Heat (1995)", 4.25),
        ("Sudden Death (1995)", 3.3333333333333335),
        ("GoldenEye (1995)", 3.0),
    ]

    expected_top_3_genres = [
        ("action", 3.527777777777778),
        ("comedy", 3.5),
        ("adventure", 3.361111111111111),
    ]

    expected_user_top_genre = "Comedy"
    expected_recommendations = []

    # --------------------------------------------------
    # Test movie averages
    # --------------------------------------------------
    movie_avgs = compute_movie_avg_ratings(ratings)
    check_dict_floats("compute_movie_avg_ratings", movie_avgs, expected_movie_avgs)

    # --------------------------------------------------
    # Test top movies overall
    # --------------------------------------------------
    actual_top_5_movies = top_n_movies(movie_avgs, movies_by_name_norm, 5)
    check_equal("top_n_movies top 5", actual_top_5_movies, expected_top_5_movies)

    # --------------------------------------------------
    # Test top movies in Action
    # --------------------------------------------------
    actual_top_action = top_n_movies_in_genre(
        movie_avgs,
        "Action",
        movies_by_name_norm,
        genre_to_movies_norm,
        3
    )
    check_equal("top_n_movies_in_genre Action", actual_top_action, expected_top_action)

    # --------------------------------------------------
    # Test genre popularity
    # --------------------------------------------------
    gpop = compute_genre_popularity(movie_avgs, movies_by_name_norm)
    check_dict_floats("compute_genre_popularity", gpop, expected_genre_popularity)

    # --------------------------------------------------
    # Test top genres
    # --------------------------------------------------
    actual_top_genres = top_n_genres(gpop, genre_to_movies_norm, 3)
    check_equal("top_n_genres top 3", actual_top_genres, expected_top_3_genres)

    # --------------------------------------------------
    # Test user top genre
    # User 6 ratings:
    # Adventure -> Jumanji 4.0, Tom and Huck 3.0 => 3.5
    # Comedy -> Grumpier 5.0, Waiting 3.0, Father 5.0 => 4.333...
    # Action -> Heat 4.0, GoldenEye 3.0 => 3.5
    # So top genre = Comedy
    # --------------------------------------------------
    actual_user_top_genre = user_top_genre(ratings, movies_by_name_norm, TEST_USER_ID)
    check_string_case_insensitive(
        "user_top_genre user 6",
        actual_user_top_genre,
        expected_user_top_genre
    )

    # --------------------------------------------------
    # Test recommendations
    # If recommendations are based on favorite genre only,
    # user 6 has already rated all Comedy movies, so result
    # should be empty.
    # --------------------------------------------------
    actual_recommendations = recommend_movies_for_user(
        ratings,
        movies_by_name_norm,
        genre_to_movies_norm,
        TEST_USER_ID,
        k=3
    )
    check_equal("recommend_movies_for_user user 6", actual_recommendations, expected_recommendations)

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------
    print("\n--- Test Summary ---")
    print(f"Passed {tests_passed} out of {tests_run} tests.")


if __name__ == "__main__":
    main()