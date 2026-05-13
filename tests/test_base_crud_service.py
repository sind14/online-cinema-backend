import pytest
from fastapi import HTTPException, status
from app.services.genre import GenreService


def test_get_all_returns_empty_list(db_session):
    result = GenreService.get_all(db_session)

    assert result == []


def test_get_all_returns_all_genres(db_session, genre_factory):
    genre_factory(name="Action")
    result = GenreService.get_all(db_session)

    assert len(result) == 1
    assert result[0].name == "Action"


def test_get_by_id_returns_genre(db_session, genre_factory):
    genre = genre_factory(name="Adventure")
    result = GenreService.get_by_id(db_session, genre.id)

    assert result == genre


def test_get_by_id_returns_none_for_nonexistent_id(db_session):
    result = GenreService.get_by_id(db_session, 999)

    assert result is None


def test_get_or_404_returns_genre(db_session, genre_factory):
    genre = genre_factory(name="Sci-Fi")
    result = GenreService.get_or_404(db_session, genre.id)

    assert result == genre


def test_get_or_404_raises_for_nonexistent_id(db_session):
    with pytest.raises(HTTPException) as exc_info:
        GenreService.get_or_404(db_session, 999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Genre with id 999 not found"


def test_create_genre(db_session):
    new_genre = GenreService.create(db_session, name="Comedy")

    assert new_genre.id is not None
    assert new_genre.name == "Comedy"


def test_create_genre_raises_for_existing_name(db_session, genre_factory):
    genre = genre_factory(name="Horror")
    with pytest.raises(HTTPException) as exc_info:
        GenreService.create(db_session, name=genre.name)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Genre with this name already exists"


def test_update_genre(db_session, genre_factory):
    genre = genre_factory(name="Thriller")
    updated_genre = GenreService.update(db_session, genre, name="Drama")

    assert updated_genre.name == "Drama"
    assert updated_genre.id == genre.id


def test_update_genre_with_none_value_does_not_change_field(db_session, genre_factory):
    genre = genre_factory(name="Romance")
    updated_genre = GenreService.update(db_session, genre, name=None)

    assert updated_genre.name == genre.name
    assert updated_genre.id == genre.id


def test_delete_genre_removes_genre_from_database(db_session, genre_factory):
    genre = genre_factory(name="Fantasy")
    GenreService.delete(db_session, genre)
    deleted_genre = GenreService.get_by_id(db_session, genre.id)

    assert deleted_genre is None
