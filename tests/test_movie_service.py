import pytest
from fastapi import HTTPException, status
from app.services.movie import MovieService
from app.schemas.movie import MovieUpdate


def test_get_all_returns_empty_result(db_session):
    result = MovieService.get_all(db_session)

    assert result["total"] == 0
    assert result["items"] == []
    assert result["page"] == 1
    assert result["page_size"] == 10
    assert result["total_pages"] == 1


def test_get_all_returns_movies(db_session, movie_factory):
    movie_factory(name="Test Movie")
    result = MovieService.get_all(db_session)

    assert result["total"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0].name == "Test Movie"


def test_get_all_filters_by_search(db_session, movie_factory):
    movie_factory(name="Mask")
    movie_factory(name="Spider-Man")

    result = MovieService.get_all(db_session, search="Man")

    assert result["total"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0].name == "Spider-Man"


def test_get_all_filters_by_year(db_session, movie_factory):
    movie_factory(name="Movie 1", year=2018)
    movie_factory(name="Movie 2", year=2019)
    movie_factory(name="Movie 3", year=2020)

    result = MovieService.get_all(db_session, year=2019)

    assert result["total"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0].name == "Movie 2"


def test_get_all_sorts_movies_by_year_desc(db_session, movie_factory):
    movie_factory(name="Movie 1", year=2018)
    movie_factory(name="Movie 2", year=2019)
    movie_factory(name="Movie 3", year=2020)

    result = MovieService.get_all(db_session, sort_by="year", order="desc")

    assert result["items"][0].name == "Movie 3"
    assert result["items"][1].name == "Movie 2"
    assert result["items"][2].name == "Movie 1"


def test_get_all_sorts_movies_by_year_asc(db_session, movie_factory):
    movie_factory(name="Movie 1", year=2018)
    movie_factory(name="Movie 2", year=2019)
    movie_factory(name="Movie 3", year=2020)

    result = MovieService.get_all(db_session, sort_by="year", order="asc")

    assert result["items"][0].name == "Movie 1"
    assert result["items"][1].name == "Movie 2"
    assert result["items"][2].name == "Movie 3"


def test_get_all_raises_for_invalid_sort_field(db_session):
    with pytest.raises(HTTPException) as exc_info:
        MovieService.get_all(db_session, sort_by="invalid_field")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Invalid sort field: invalid_field"


def test_get_all_returns_first_page_results(db_session, movie_factory):
    movie_factory(name="Movie 1")
    movie_factory(name="Movie 2")

    result = MovieService.get_all(db_session, page=1, page_size=1, sort_by="id", order="asc")

    assert result["total"] == 2
    assert len(result["items"]) == 1
    assert result["items"][0].name == "Movie 1"


def test_get_all_returns_second_page_results(db_session, movie_factory):
    movie_factory(name="Movie 1")
    movie_factory(name="Movie 2")

    result = MovieService.get_all(db_session, page=2, page_size=1, sort_by="id", order="asc")

    assert result["total"] == 2
    assert len(result["items"]) == 1
    assert result["items"][0].name == "Movie 2"


def test_create_movie(db_session, movie_create_data_factory):
    data = movie_create_data_factory()

    movie = MovieService.create_movie(db_session, data)

    assert movie.name == "Test Movie"
    assert movie.year == 2023

    assert len(movie.stars) == 1
    assert len(movie.directors) == 1
    assert len(movie.genres) == 1

    assert movie.certification is not None


def test_create_movie_raises_for_invalid_certification(db_session, movie_create_data_factory):
    data = movie_create_data_factory(certification_id=999)

    with pytest.raises(HTTPException) as exc_info:
        MovieService.create_movie(db_session, data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Invalid certification id"


def test_create_movie_raises_for_invalid_genre_ids(db_session, movie_create_data_factory):
    data = movie_create_data_factory(genre_ids=[999])
    with pytest.raises(HTTPException) as exc_info:
        MovieService.create_movie(db_session, data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "One or more genre_ids are invalid"


def test_create_movie_raises_for_invalid_director_ids(db_session, movie_create_data_factory):
    data = movie_create_data_factory(director_ids=[999])
    with pytest.raises(HTTPException) as exc_info:
        MovieService.create_movie(db_session, data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "One or more director_ids are invalid"


def test_create_movie_raises_for_invalid_star_ids(db_session, movie_create_data_factory):
    data = movie_create_data_factory(star_ids=[999])
    with pytest.raises(HTTPException) as exc_info:
        MovieService.create_movie(db_session, data)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "One or more star_ids are invalid"


def test_create_movie_with_multiple_relationships(
        db_session,
        movie_create_data_factory,
        genre_factory,
        star_factory,
        director_factory,
):
    genre1 = genre_factory(name="Genre 1")
    genre2 = genre_factory(name="Genre 2")

    star1 = star_factory(name="Actor 1")
    star2 = star_factory(name="Actor 2")

    director1 = director_factory(name="Director 1")
    director2 = director_factory(name="Director 2")

    data = movie_create_data_factory(
        genre_ids=[genre1.id, genre2.id],
        star_ids=[star1.id, star2.id],
        director_ids=[director1.id, director2.id],
    )

    movie = MovieService.create_movie(db_session, data)

    assert len(movie.genres) == 2
    assert len(movie.stars) == 2
    assert len(movie.directors) == 2

    assert genre1 in movie.genres
    assert genre2 in movie.genres

    assert star1 in movie.stars
    assert star2 in movie.stars

    assert director1 in movie.directors
    assert director2 in movie.directors


def test_update_movie(db_session, movie_create_data_factory):
    movie = MovieService.create_movie(db_session, movie_create_data_factory())

    update_data = MovieUpdate(
        name="Updated Movie",
        year=2024,
        time=130,
        imdb=8.5,
        votes=1000,
        description="A new description",
    )

    updated_movie = MovieService.update_movie(db_session, movie, update_data)

    assert updated_movie.name == "Updated Movie"
    assert updated_movie.year == 2024
    assert updated_movie.time == 130
    assert updated_movie.imdb == 8.5
    assert updated_movie.votes == 1000
    assert updated_movie.description == "A new description"


def test_update_movie_with_relationships(
        db_session,
        movie_create_data_factory,
        genre_factory, star_factory,
        director_factory,
):
    movie = MovieService.create_movie(db_session, movie_create_data_factory())
    old_genre = movie.genres[0]
    old_star = movie.stars[0]
    old_director = movie.directors[0]
    new_genre = genre_factory(name="New Genre")
    new_star = star_factory(name="New Star")
    new_director = director_factory(name="New Director")

    update_data = MovieUpdate(
        genre_ids=[new_genre.id],
        star_ids=[new_star.id],
        director_ids=[new_director.id],
    )

    updated_movie = MovieService.update_movie(db_session, movie, update_data)

    assert len(updated_movie.genres) == 1
    assert len(updated_movie.stars) == 1
    assert len(updated_movie.directors) == 1

    assert new_genre in updated_movie.genres
    assert new_star in updated_movie.stars
    assert new_director in updated_movie.directors

    assert old_genre not in updated_movie.genres
    assert old_star not in updated_movie.stars
    assert old_director not in updated_movie.directors


def test_update_movie_with_partial_update(db_session, movie_create_data_factory):
    movie = MovieService.create_movie(db_session, movie_create_data_factory())
    update_data = MovieUpdate(name="Updated Movie")
    updated_movie = MovieService.update_movie(db_session, movie, update_data)
    assert updated_movie.name == "Updated Movie"
    assert updated_movie.year == movie.year
    assert updated_movie.time == movie.time
    assert updated_movie.imdb == movie.imdb
    assert updated_movie.votes == movie.votes
    assert updated_movie.description == movie.description
