from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set


@dataclass(frozen=True)
class Movie:
    """Represents a single movie record from the movies file."""
    genre: str
    movie_id: str
    name: str


def _normalize_key(s: str) -> str:
    """
    Normalize identifiers that should be treated case-insensitively.
    We normalize movie_name and genre to lower-case for consistent matching.

    Note: We still store/display original movie names as seen in file.
    """
    return s.strip().casefold()


def load_movies(movies_path: str) -> Tuple[Dict[str, Movie], Dict[str, List[str]]]:
    """
    Load movies from a movies file.

    Returns:
        movies_by_name_norm: dict normalized_movie_name -> Movie
        genre_to_movies_norm: dict normalized_genre -> list of normalized_movie_name

    Robustness:
    - Skips blank lines.
    - Skips malformed lines that don't have exactly 3 fields.
    - Trims whitespace around fields.
    - If duplicate movie names appear, the last one wins.
    """
    movies_by_name_norm: Dict[str, Movie] = {}
    genre_to_movies_norm: Dict[str, List[str]] = {}

    with open(movies_path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) != 3:
                # malformed line
                continue
            genre, movie_id, movie_name = (p.strip() for p in parts)
            if not genre or not movie_id or not movie_name:
                continue

            name_norm = _normalize_key(movie_name)
            genre_norm = _normalize_key(genre)

            movie = Movie(genre=genre, movie_id=movie_id, name=movie_name)
            movies_by_name_norm[name_norm] = movie

            genre_to_movies_norm.setdefault(genre_norm, [])
            if name_norm not in genre_to_movies_norm[genre_norm]:
                genre_to_movies_norm[genre_norm].append(name_norm)

    return movies_by_name_norm, genre_to_movies_norm


def load_ratings(ratings_path: str) -> List[Tuple[str, float, str]]:
    """
    Load ratings from a ratings file.

    Returns:
        List of tuples: (normalized_movie_name, rating_float, user_id_str)

    Robustness:
    - Skips blank lines.
    - Skips malformed lines not having exactly 3 fields.
    - Skips ratings that can't be parsed as float.
    - Skips ratings outside [0, 5].
    """
    ratings: List[Tuple[str, float, str]] = []

    with open(ratings_path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) != 3:
                continue
            movie_name, rating_str, user_id = (p.strip() for p in parts)
            if not movie_name or not rating_str or not user_id:
                continue
            try:
                rating = float(rating_str)
            except ValueError:
                continue
            if rating < 0 or rating > 5:
                continue

            ratings.append((_normalize_key(movie_name), rating, user_id))

    return ratings


def compute_movie_avg_ratings(ratings: List[Tuple[str, float, str]]) -> Dict[str, float]:
    """
    Compute average rating per movie from ratings list.

    Args:
        ratings: list of (movie_name_norm, rating, user_id)

    Returns:
        dict movie_name_norm -> average_rating (float)
    """
    sums: Dict[str, float] = {}
    counts: Dict[str, int] = {}

    for movie_norm, rating, _uid in ratings:
        sums[movie_norm] = sums.get(movie_norm, 0.0) + rating
        counts[movie_norm] = counts.get(movie_norm, 0) + 1

    avgs: Dict[str, float] = {}
    for m in sums:
        avgs[m] = sums[m] / counts[m]
    return avgs


def top_n_movies(movie_avgs: Dict[str, float],
                 movies_by_name_norm: Dict[str, Movie],
                 n: int) -> List[Tuple[str, float]]:
    """
    Return the top n movies ranked by average rating (descending).
    Ties are broken alphabetically by movie name (original display name).

    Returns:
        list of (movie_display_name, avg_rating)
    """
    items: List[Tuple[str, float]] = []
    for m_norm, avg in movie_avgs.items():
        display = movies_by_name_norm[m_norm].name if m_norm in movies_by_name_norm else m_norm
        items.append((display, avg))

    items.sort(key=lambda x: (-x[1], x[0].casefold()))
    return items[: max(0, n)]


def top_n_movies_in_genre(movie_avgs: Dict[str, float],
                          genre: str,
                          movies_by_name_norm: Dict[str, Movie],
                          genre_to_movies_norm: Dict[str, List[str]],
                          n: int) -> List[Tuple[str, float]]:
    """
    Return the top n movies in a given genre ranked by average rating (descending).

    Args:
        genre: user-provided genre string (case-insensitive)

    Returns:
        list of (movie_display_name, avg_rating)
    """
    genre_norm = _normalize_key(genre)
    movie_list = genre_to_movies_norm.get(genre_norm, [])

    items: List[Tuple[str, float]] = []
    for m_norm in movie_list:
        if m_norm in movie_avgs:
            display = movies_by_name_norm[m_norm].name
            items.append((display, movie_avgs[m_norm]))

    items.sort(key=lambda x: (-x[1], x[0].casefold()))
    return items[: max(0, n)]


def compute_genre_popularity(movie_avgs: Dict[str, float],
                             movies_by_name_norm: Dict[str, Movie]) -> Dict[str, float]:
    """
    Compute genre popularity: for each genre, take the average of
    (average ratings of movies in that genre).

    Returns:
        dict genre_norm -> genre_popularity_score
    """
    genre_sums: Dict[str, float] = {}
    genre_counts: Dict[str, int] = {}

    for m_norm, avg in movie_avgs.items():
        movie = movies_by_name_norm.get(m_norm)
        if movie is None:
            continue
        g_norm = _normalize_key(movie.genre)
        genre_sums[g_norm] = genre_sums.get(g_norm, 0.0) + avg
        genre_counts[g_norm] = genre_counts.get(g_norm, 0) + 1

    genre_avgs: Dict[str, float] = {}
    for g in genre_sums:
        genre_avgs[g] = genre_sums[g] / genre_counts[g]
    return genre_avgs


def top_n_genres(genre_popularity: Dict[str, float],
                 genre_to_movies_norm: Dict[str, List[str]],
                 n: int) -> List[Tuple[str, float]]:
    """
    Return top n genres ranked by popularity score (descending).
    Ties broken alphabetically by genre name (normalized).

    Returns:
        list of (genre_display_name, popularity_score)
    """
    items = [(g, score) for g, score in genre_popularity.items()]
    items.sort(key=lambda x: (-x[1], x[0]))
    # Display: use original casing? We only have normalized; keep normalized.
    return [(g, score) for g, score in items[: max(0, n)]]


def user_genre_preference(ratings: List[Tuple[str, float, str]],
                          movies_by_name_norm: Dict[str, Movie],
                          user_id: str) -> Dict[str, float]:
    """
    Compute user's preference for each genre:
    For each genre, compute the average of the user's ratings of movies in that genre.

    Returns:
        dict genre_norm -> user_avg_rating_in_genre
    """
    sums: Dict[str, float] = {}
    counts: Dict[str, int] = {}

    for m_norm, rating, uid in ratings:
        if uid != user_id:
            continue
        movie = movies_by_name_norm.get(m_norm)
        if movie is None:
            continue
        g_norm = _normalize_key(movie.genre)
        sums[g_norm] = sums.get(g_norm, 0.0) + rating
        counts[g_norm] = counts.get(g_norm, 0) + 1

    avgs: Dict[str, float] = {}
    for g in sums:
        avgs[g] = sums[g] / counts[g]
    return avgs


def user_top_genre(ratings: List[Tuple[str, float, str]],
                   movies_by_name_norm: Dict[str, Movie],
                   user_id: str) -> Optional[str]:
    """
    Return the normalized genre most preferred by the user.
    If user has no valid ratings, return None.

    Ties broken alphabetically by genre_norm.
    """
    prefs = user_genre_preference(ratings, movies_by_name_norm, user_id)
    if not prefs:
        return None
    items = list(prefs.items())
    items.sort(key=lambda x: (-x[1], x[0]))
    return items[0][0]


def recommend_movies_for_user(ratings: List[Tuple[str, float, str]],
                              movies_by_name_norm: Dict[str, Movie],
                              genre_to_movies_norm: Dict[str, List[str]],
                              user_id: str,
                              k: int = 3) -> List[Tuple[str, float]]:
    """
    Recommend up to k movies:
    - find user's top genre
    - get most popular movies (by average rating) within that genre
    - exclude movies user has already rated
    - return up to k (movie_display_name, avg_rating)

    If user has no top genre, return empty list.
    """
    top_g = user_top_genre(ratings, movies_by_name_norm, user_id)
    if top_g is None:
        return []

    movie_avgs = compute_movie_avg_ratings(ratings)

    rated_by_user: Set[str] = {m for (m, _r, uid) in ratings if uid == user_id}

    candidates_norm = genre_to_movies_norm.get(top_g, [])
    items: List[Tuple[str, float]] = []
    for m_norm in candidates_norm:
        if m_norm in rated_by_user:
            continue
        if m_norm not in movie_avgs:
            continue
        display = movies_by_name_norm[m_norm].name
        items.append((display, movie_avgs[m_norm]))

    items.sort(key=lambda x: (-x[1], x[0].casefold()))
    return items[: max(0, k)]


# ---------------- CLI ----------------

def _print_menu() -> None:
    print("\n=== Movie Recommender CLI ===")
    print("1) Load movies file")
    print("2) Load ratings file")
    print("3) Show top N movies (overall)")
    print("4) Show top N movies in a genre")
    print("5) Show top N genres")
    print("6) Show user's top genre")
    print("7) Recommend movies for a user")
    print("0) Quit")


def main() -> None:
    movies_by_name_norm: Dict[str, Movie] = {}
    genre_to_movies_norm: Dict[str, List[str]] = {}
    ratings: List[Tuple[str, float, str]] = []

    while True:
        _print_menu()
        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("Goodbye.")
            return

        if choice == "1":
            path = input("Enter movies file path: ").strip()
            try:
                movies_by_name_norm, genre_to_movies_norm = load_movies(path)
                print(f"Loaded {len(movies_by_name_norm)} movies.")
            except OSError as e:
                print(f"Error loading movies file: {e}")

        elif choice == "2":
            path = input("Enter ratings file path: ").strip()
            try:
                ratings = load_ratings(path)
                print(f"Loaded {len(ratings)} ratings.")
            except OSError as e:
                print(f"Error loading ratings file: {e}")

        elif choice == "3":
            if not ratings:
                print("Load ratings first.")
                continue
            if not movies_by_name_norm:
                print("Load movies first.")
                continue
            n = int(input("Enter N: ").strip())
            movie_avgs = compute_movie_avg_ratings(ratings)
            result = top_n_movies(movie_avgs, movies_by_name_norm, n)
            for name, avg in result:
                print(f"{name}: {avg}")

        elif choice == "4":
            if not ratings:
                print("Load ratings first.")
                continue
            if not movies_by_name_norm:
                print("Load movies first.")
                continue
            genre = input("Enter genre: ").strip()
            n = int(input("Enter N: ").strip())
            movie_avgs = compute_movie_avg_ratings(ratings)
            result = top_n_movies_in_genre(movie_avgs, genre, movies_by_name_norm, genre_to_movies_norm, n)
            for name, avg in result:
                print(f"{name}: {avg}")

        elif choice == "5":
            if not ratings:
                print("Load ratings first.")
                continue
            if not movies_by_name_norm:
                print("Load movies first.")
                continue
            n = int(input("Enter N: ").strip())
            movie_avgs = compute_movie_avg_ratings(ratings)
            gpop = compute_genre_popularity(movie_avgs, movies_by_name_norm)
            result = top_n_genres(gpop, genre_to_movies_norm, n)
            for g, score in result:
                print(f"{g}: {score}")

        elif choice == "6":
            if not ratings:
                print("Load ratings first.")
                continue
            if not movies_by_name_norm:
                print("Load movies first.")
                continue
            user_id = input("Enter user id: ").strip()
            tg = user_top_genre(ratings, movies_by_name_norm, user_id)
            print("Top genre:", tg if tg is not None else "(none)")

        elif choice == "7":
            if not ratings:
                print("Load ratings first.")
                continue
            if not movies_by_name_norm:
                print("Load movies first.")
                continue
            user_id = input("Enter user id: ").strip()
            recs = recommend_movies_for_user(ratings, movies_by_name_norm, genre_to_movies_norm, user_id, k=3)
            if not recs:
                print("(no recommendations)")
            else:
                for name, avg in recs:
                    print(f"{name}: {avg}")

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()