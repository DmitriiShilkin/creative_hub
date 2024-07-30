import json
from io import BytesIO
from typing import Callable

from fastapi import UploadFile
from httpx import AsyncClient

from models import (
    City,
    Event,
    Organisation,
    Specialization,
    Timezone,
    User,
    Favorite,
)

ROOT_ENDPOINT = "/ch/v1/event/"


class TestEvent:
    async def test_read_event_author(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_fixture: Event,
    ):
        endpoint = f"{ROOT_ENDPOINT}author/{user_fixture.uid}/"
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 200

        try:
            response_data = response.json()
            assert response_data["objects"][0]["title"] == event_fixture.title
            assert (
                response_data["objects"][0]["description"]
                == event_fixture.description
            )
        except KeyError as e:
            error_message = f"Отсутствует ожидаемое поле в ответе: {e}"
            raise AssertionError(error_message) from None

    async def test_read_authors_events_with_favorite_filter(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        user_fixture_2: User,
        event_fixture: Event,
        event_favorites_list_fixture: Favorite,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}author/{user_fixture.uid}/"
        response = await http_client.get(
            endpoint, headers=user_auth_headers, params={"favorite": True}
        )
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert len(response_data["objects"]) == 1, response_data
        assert (
            event_fixture.id == response_data["objects"][0]["id"]
        ), response_data
        assert response_data["objects"][0]["is_favorite"] is True
        assert response_data["objects"][0]["is_attended"] is True

    async def test_read_event_author_by_wrong_uid(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        author_uid = "12345678-1234-5678-1234-567812345678"
        endpoint = f"{ROOT_ENDPOINT}author/{author_uid}/"
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 404, response.text

    async def test_read_event(
        self,
        user_fixture: User,
        get_auth_headers: Callable,
        http_client: AsyncClient,
        event_fixture: Event,
    ):
        endpoint = f"{ROOT_ENDPOINT}"
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200, response.text

        try:
            response_data = response.json()
            assert response_data["objects"][0]["title"] == event_fixture.title
            assert (
                response_data["objects"][0]["description"]
                == event_fixture.description
            )
            for event in response_data["objects"]:
                assert event["is_favorite"] is False
        except KeyError as e:
            error_message = f"Отсутствует ожидаемое поле в ответе: {e}"
            raise AssertionError(error_message) from None

    async def test_read_event_with_favorite_filter(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture_2: User,
        event_fixture: Event,
        event_favorites_list_fixture: Favorite,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        response = await http_client.get(
            ROOT_ENDPOINT, headers=user_auth_headers, params={"favorite": True}
        )
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert len(response_data["objects"]) == 1, response_data
        assert (
            event_fixture.id == response_data["objects"][0]["id"]
        ), response_data
        assert response_data["objects"][0]["is_favorite"] is True
        assert response_data["objects"][0]["is_attended"] is True

    async def test_get_single_event(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_fixture: Event,
    ):
        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/"
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200, [response.text, event_fixture.id]

        try:
            response_data = response.json()
            assert response_data["id"] == event_fixture.id
            assert response_data["title"] == event_fixture.title
            assert response_data["description"] == event_fixture.description
        except KeyError as e:
            error_message = f"Отсутствует ожидаемое поле в ответе: {e}"
            raise AssertionError(error_message) from None

    async def test_read_favorite_event(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture_2: User,
        event_fixture: Event,
        event_favorites_list_fixture: Favorite,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["is_favorite"] is True
        assert response_data["is_attended"] is True
        assert response_data["title"] == event_fixture.title
        assert response_data["id"] == event_fixture.id

    async def test_get_single_event_by_wrong_id(
        self,
        http_client: AsyncClient,
    ):
        non_existent_event_id = 999999999
        endpoint = f"{ROOT_ENDPOINT}{non_existent_event_id}/"
        response = await http_client.get(endpoint)
        assert response.status_code == 404, response.text

    async def test_event_delete(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
        event_fixture: Event,
    ):
        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/"
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.delete(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 204, response.text

    async def test_delete_event_unauthorized(
        self,
        http_client: AsyncClient,
        event_fixture: Event,
    ):
        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/"
        response = await http_client.delete(endpoint)
        assert response.status_code == 401, response.text

    async def test_delete_event_by_wrong_id(
        self,
        get_auth_headers: Callable,
        user_fixture: User,
        http_client: AsyncClient,
    ):
        non_existent_event_id = 999999999
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{non_existent_event_id}/"
        response = await http_client.delete(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 404, response.text

    async def test_create_event(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        user_fixture_2: User,
        city_fixture: City,
        specialization_fixture_2: Specialization,
        organisation_fixture: Organisation,
        timezone_fixture: Timezone,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)

        photo = UploadFile(
            filename="photo.jpg", file=BytesIO(b"fake_image_data")
        )
        event_cover = UploadFile(
            filename="cover.jpg", file=BytesIO(b"fake_cover_data")
        )

        event_data = json.dumps(
            {
                "title": "Creativehub Fest",
                "description": "KH SUMMER FEST",
                "language": "German",
                "extra_languages": ["English", "French"],
                "event_type": "Festival",
                "is_free": True,
                "is_online": False,
                "city_id": city_fixture.id,
                "places": [
                    {
                        "address": "123 Creative St, Cityville",
                        "place_name": "Village",
                    }
                ],
                "online_links": ["https://wwww.creativehub.com/"],
                "start_datetime": "2024-11-15T06:49:19.667Z",
                "end_datetime": "2024-11-25T06:49:19.667Z",
                "registration_end_type": "At event start",
                "reminders": [
                    {"reminder_before_event": 1, "reminder_unit": "minutes"}
                ],
                "specializations_ids": [specialization_fixture_2.id],
                "speakers_uids": [str(user_fixture.uid)],
                "organisations_ids": [organisation_fixture.id],
                "organizers_uids": [str(user_fixture_2.uid)],
                "is_draft": False,
                "is_archived": False,
                "timezone": {"tzcode": "string2", "utc": "string"},
            }
        )

        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={
                "create_data": event_data,
                "contact_person_data": contact_person_data,
            },
            files={
                "photo": (photo.filename, photo.file, photo.content_type),
                "event_cover": (
                    event_cover.filename,
                    event_cover.file,
                    event_cover.content_type,
                ),
            },
        )
        assert response.status_code == 201, response.text
        response_data = response.json()
        assert "Creativehub Fest" in response_data["title"]
        assert response_data["online_links"] == [
            "https://wwww.creativehub.com/"
        ]
        assert len(response_data["organizers"]) == 2

    async def test_create_event_with_language_in_extra_languages(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        city_fixture: City,
        specialization_fixture_2: Specialization,
        organisation_fixture: Organisation,
        timezone_fixture: Timezone,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)

        photo = UploadFile(
            filename="photo.jpg", file=BytesIO(b"fake_image_data")
        )
        event_cover = UploadFile(
            filename="cover.jpg", file=BytesIO(b"fake_cover_data")
        )

        event_data = json.dumps(
            {
                "title": "Creativehub Fest",
                "description": "KH SUMMER FEST",
                "language": "German",
                "extra_languages": ["English", "German"],
                "event_type": "Festival",
                "is_free": True,
                "is_online": False,
                "city_id": city_fixture.id,
                "places": [
                    {
                        "address": "123 Creative St, Cityville",
                        "place_name": "Village",
                    }
                ],
                "online_links": ["https://wwww.creativehub.com/"],
                "start_datetime": "2024-11-15T06:49:19.667Z",
                "end_datetime": "2024-11-25T06:49:19.667Z",
                "registration_end_type": "At event start",
                "reminders": [
                    {"reminder_before_event": 1, "reminder_unit": "minutes"}
                ],
                "specializations_ids": [specialization_fixture_2.id],
                "speakers_uids": [str(user_fixture.uid)],
                "organisations_ids": [organisation_fixture.id],
                "organizers_uids": [str(user_fixture.uid)],
                "is_draft": False,
                "is_archived": False,
                "timezone": {"tzcode": "string2", "utc": "string"},
            }
        )

        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={
                "create_data": event_data,
                "contact_person_data": contact_person_data,
            },
            files={
                "photo": (photo.filename, photo.file, photo.content_type),
                "event_cover": (
                    event_cover.filename,
                    event_cover.file,
                    event_cover.content_type,
                ),
            },
        )
        assert response.status_code == 422

    async def test_create_event_with_start_datetime_without_tz(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        city_fixture: City,
        specialization_fixture_2: Specialization,
        organisation_fixture: Organisation,
        timezone_fixture: Timezone,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)

        photo = UploadFile(
            filename="photo.jpg", file=BytesIO(b"fake_image_data")
        )
        event_cover = UploadFile(
            filename="cover.jpg", file=BytesIO(b"fake_cover_data")
        )

        event_data = json.dumps(
            {
                "title": "Creativehub Fest",
                "description": "KH SUMMER FEST",
                "language": "German",
                "extra_languages": ["English", "French"],
                "event_type": "Festival",
                "is_free": True,
                "is_online": False,
                "city_id": city_fixture.id,
                "places": [
                    {
                        "address": "123 Creative St, Cityville",
                        "place_name": "Village",
                    }
                ],
                "online_links": ["https://wwww.creativehub.com/"],
                "start_datetime": "2024-11-15T06:49:19.667",
                "end_datetime": "2024-11-25T06:49:19.667Z",
                "registration_end_type": "At event start",
                "reminders": [
                    {"reminder_before_event": 1, "reminder_unit": "minutes"}
                ],
                "specializations_ids": [specialization_fixture_2.id],
                "speakers_uids": [str(user_fixture.uid)],
                "organisations_ids": [organisation_fixture.id],
                "organizers_uids": [str(user_fixture.uid)],
                "is_draft": False,
                "is_archived": False,
                "timezone": {"tzcode": "string2", "utc": "string"},
            }
        )

        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={
                "create_data": event_data,
                "contact_person_data": contact_person_data,
            },
            files={
                "photo": (photo.filename, photo.file, photo.content_type),
                "event_cover": (
                    event_cover.filename,
                    event_cover.file,
                    event_cover.content_type,
                ),
            },
        )
        assert response.status_code == 201, response.text
        response_data = response.json()
        assert "Creativehub Fest" in response_data["title"]
        assert response_data["online_links"] == [
            "https://wwww.creativehub.com/"
        ]

    async def test_create_event_with_invalid_registration_end_datetime(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        city_fixture: City,
        specialization_fixture_2: Specialization,
        organisation_fixture: Organisation,
        timezone_fixture: Timezone,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)

        photo = UploadFile(
            filename="photo.jpg", file=BytesIO(b"fake_image_data")
        )
        event_cover = UploadFile(
            filename="cover.jpg", file=BytesIO(b"fake_cover_data")
        )

        event_data = json.dumps(
            {
                "title": "Creativehub Fest",
                "description": "KH SUMMER FEST",
                "language": "German",
                "extra_languages": ["English", "French"],
                "event_type": "Festival",
                "is_free": True,
                "is_online": False,
                "city_id": city_fixture.id,
                "places": [
                    {
                        "address": "123 Creative St, Cityville",
                        "place_name": "Village",
                    }
                ],
                "online_links": ["https://wwww.creativehub.com/"],
                "start_datetime": "2024-11-15T06:49:19.667Z",
                "end_datetime": "2024-11-25T06:49:19.667Z",
                "registration_end_type": "Custom before event",
                "registration_end_datetime": "2024-11-17T06:49:19.667Z",
                "reminders": [
                    {"reminder_before_event": 1, "reminder_unit": "minutes"}
                ],
                "specializations_ids": [specialization_fixture_2.id],
                "speakers_uids": [str(user_fixture.uid)],
                "organisations_ids": [organisation_fixture.id],
                "organizers_uids": [str(user_fixture.uid)],
                "is_draft": False,
                "is_archived": False,
                "timezone": {"tzcode": "string2", "utc": "string"},
            }
        )

        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={
                "create_data": event_data,
                "contact_person_data": contact_person_data,
            },
            files={
                "photo": (photo.filename, photo.file, photo.content_type),
                "event_cover": (
                    event_cover.filename,
                    event_cover.file,
                    event_cover.content_type,
                ),
            },
        )
        assert response.status_code == 422

    async def test_create_event_unauthorized(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        city_fixture: City,
        specialization_fixture_2: Specialization,
        organisation_fixture: Organisation,
    ) -> None:
        photo = UploadFile(
            filename="photo.jpg", file=BytesIO(b"fake_image_data")
        )
        event_cover = UploadFile(
            filename="cover.jpg", file=BytesIO(b"fake_cover_data")
        )

        event_data = json.dumps(
            {
                "title": "Creativehub Fest",
                "description": "KH SUMMER FEST",
                "language": "German",
                "extra_languages": ["English", "French"],
                "event_type": "Festival",
                "is_free": True,
                "is_online": False,
                "city_id": city_fixture.id,
                "places": [
                    {
                        "address": "123 Creative St, Cityville",
                        "place_name": "Village",
                    }
                ],
                "online_links": ["https://wwww.creativehub.com/"],
                "start_datetime": "2024-11-15T06:49:19.667Z",
                "end_datetime": "2024-11-25T06:49:19.667Z",
                "registration_end_type": "At event start",
                "reminders": [
                    {"reminder_before_event": 1, "reminder_unit": "minutes"}
                ],
                "specializations_ids": [specialization_fixture_2.id],
                "speakers_uids": [str(user_fixture.uid)],
                "organisations_ids": [organisation_fixture.id],
                "organizers_uids": [str(user_fixture.uid)],
                "is_draft": False,
                "is_archived": False,
            }
        )

        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        response = await http_client.post(
            ROOT_ENDPOINT,
            data={
                "create_data": event_data,
                "contact_person_data": contact_person_data,
            },
            files={
                "photo": (photo.filename, photo.file, photo.content_type),
                "event_cover": (
                    event_cover.filename,
                    event_cover.file,
                    event_cover.content_type,
                ),
            },
        )
        assert response.status_code == 401, response.text

    async def test_create_event_with_invalid_data(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        city_fixture: City,
        specialization_fixture_2: Specialization,
        organisation_fixture: Organisation,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)

        photo = UploadFile(
            filename="photo.jpg", file=BytesIO(b"fake_image_data")
        )
        event_cover = UploadFile(
            filename="cover.jpg", file=BytesIO(b"fake_cover_data")
        )

        event_data = json.dumps(
            {
                "title": "Creativehub Fest",
                "description": "KH SUMMER FEST",
                "language": "German",
                "extra_languages": ["English", "French"],
                "event_type": "Festival",
                "is_free": 10,
                "is_online": False,
                "city_id": city_fixture.id,
                "places": [
                    {
                        "address": "123 Creative St, Cityville",
                        "place_name": "Village",
                    }
                ],
                "online_links": ["https://wwww.creativehub.com/"],
                "start_datetime": "2024-11-15T06:49:19.667Z",
                "end_datetime": "2024-11-25T06:49:19.667Z",
                "registration_end_type": "Today",
                "reminders": [
                    {"reminder_before_event": 1, "reminder_unit": "minutes"}
                ],
                "specializations_ids": [specialization_fixture_2.id],
                "speakers_uids": [str(user_fixture.uid)],
                "organisations_ids": [organisation_fixture.id],
                "organizers_uids": [str(user_fixture.uid)],
                "is_draft": False,
                "is_archived": False,
            }
        )

        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={
                "create_data": event_data,
                "contact_person_data": contact_person_data,
            },
            files={
                "photo": (photo.filename, photo.file, photo.content_type),
                "event_cover": (
                    event_cover.filename,
                    event_cover.file,
                    event_cover.content_type,
                ),
            },
        )
        assert response.status_code == 422, response.text

    async def test_create_event_with_invalid_reminders(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        city_fixture: City,
        specialization_fixture_2: Specialization,
        organisation_fixture: Organisation,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)

        photo = UploadFile(
            filename="photo.jpg", file=BytesIO(b"fake_image_data")
        )
        event_cover = UploadFile(
            filename="cover.jpg", file=BytesIO(b"fake_cover_data")
        )

        event_data = json.dumps(
            {
                "title": "Creativehub Fest",
                "description": "KH SUMMER FEST",
                "language": "German",
                "extra_languages": ["English", "French"],
                "event_type": "Festival",
                "is_free": 10,
                "is_online": False,
                "city_id": city_fixture.id,
                "places": [
                    {
                        "address": "123 Creative St, Cityville",
                        "place_name": "Village",
                    }
                ],
                "online_links": ["https://wwww.creativehub.com/"],
                "start_datetime": "2024-11-15T06:49:19.667Z",
                "end_datetime": "2024-11-25T06:49:19.667Z",
                "registration_end_type": "Today",
                "reminders": [
                    {
                        "reminder_before_event": 1,
                        "reminder_unit": "minutes",
                        "reminder_time": "10:00",
                    }
                ],
                "specializations_ids": [specialization_fixture_2.id],
                "speakers_uids": [str(user_fixture.uid)],
                "organisations_ids": [organisation_fixture.id],
                "organizers_uids": [str(user_fixture.uid)],
                "is_draft": False,
                "is_archived": False,
            }
        )

        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={
                "create_data": event_data,
                "contact_person_data": contact_person_data,
            },
            files={
                "photo": (photo.filename, photo.file, photo.content_type),
                "event_cover": (
                    event_cover.filename,
                    event_cover.file,
                    event_cover.content_type,
                ),
            },
        )
        assert response.status_code == 422, response.text

    async def test_update_event(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_fixture: Event,
        user_fixture: User,
        user_fixture_2: User,
        city_fixture: City,
        specialization_fixture_2: Specialization,
        organisation_fixture: Organisation,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)

        update_data = json.dumps(
            {
                "title": "Updated Creativehub Fest",
                "description": "Update IZI FEST",
                "language": "German",
                "extra_languages": ["English", "French"],
                "event_type": "Exhibition",
                "is_free": True,
                "is_online": False,
                "city_id": city_fixture.id,
                "places": [
                    {
                        "address": "123 Creative St, Cityville",
                        "place_name": "Village",
                    }
                ],
                "online_links": ["https://wwww.creativehub.com/"],
                "start_datetime": "2024-11-15T06:49:19.667Z",
                "end_datetime": "2024-11-25T06:49:19.667Z",
                "registration_end_type": "At event start",
                "reminders": [
                    {"reminder_before_event": 1, "reminder_unit": "minutes"}
                ],
                "specializations_ids": [specialization_fixture_2.id],
                "speakers_uids": [str(user_fixture.uid)],
                "organisations_ids": [organisation_fixture.id],
                "organizers_uids": [str(user_fixture_2.uid)],
                "is_draft": False,
                "is_archived": False,
            }
        )

        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": update_data,
                "contact_person_data": contact_person_data,
            },
        )
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert "Updated Creativehub Fest" in response_data["title"]
        assert response_data["event_type"] == "Exhibition"

    async def test_archive_draft_event(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_fixture_2: Event,
        user_fixture: User,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)

        update_data = json.dumps(
            {
                "is_draft": True,
                "is_archived": True,
            }
        )

        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        endpoint = f"{ROOT_ENDPOINT}{event_fixture_2.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": update_data,
                "contact_person_data": contact_person_data,
            },
        )
        assert response.status_code == 409

    async def test_update_event_with_is_draft(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_fixture_2: Event,
        user_fixture: User,
    ) -> None:
        endpoint = f"{ROOT_ENDPOINT}{event_fixture_2.id}/"
        user_auth_headers = await get_auth_headers(user_fixture)
        update_data = json.dumps({"is_draft": False})
        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": update_data,
                "contact_person_data": contact_person_data,
            },
        )
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert response_data["is_draft"] is False

    async def test_update_event_with_invalid_organizers_uids(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_fixture_2: Event,
        user_fixture: User,
    ) -> None:
        endpoint = f"{ROOT_ENDPOINT}{event_fixture_2.id}/"
        user_auth_headers = await get_auth_headers(user_fixture)
        update_data = json.dumps({"organizers_uids": [], "is_draft": False})
        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": update_data,
                "contact_person_data": contact_person_data,
            },
        )
        assert response.status_code == 409

    async def test_update_draft_event_with_fields_reset(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_fixture_2: Event,
        user_fixture: User,
    ) -> None:
        endpoint = f"{ROOT_ENDPOINT}{event_fixture_2.id}/"
        user_auth_headers = await get_auth_headers(user_fixture)
        update_data = json.dumps(
            {
                "extra_languages": [],
                "places": [],
                "online_links": [],
                "reminders": [],
                "specializations_ids": [],
                "speakers_uids": [],
                "organisations_ids": [],
                "organizers_uids": [],
                "is_draft": True,
            }
        )
        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": update_data,
                "contact_person_data": contact_person_data,
            },
        )
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert response_data["extra_languages"] == []
        assert response_data["places"] == []
        assert response_data["online_links"] == []
        assert response_data["reminders"] == []
        assert response_data["specializations"] == []
        assert response_data["speakers"] == []
        assert response_data["organisations"] == []
        assert response_data["organizers"] == []

    async def test_update_event_with_invalid_language(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_fixture: Event,
        user_fixture: User,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        update_data = json.dumps(
            {
                "language": "French",
                "is_draft": False,
                "is_archived": False,
            }
        )
        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": update_data,
                "contact_person_data": contact_person_data,
            },
        )
        assert response.status_code == 422

    async def test_update_event_with_invalid_extra_languages(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_fixture: Event,
        user_fixture: User,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        update_data = json.dumps(
            {
                "extra_languages": ["English", "French"],
                "is_draft": False,
                "is_archived": False,
            }
        )
        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": update_data,
                "contact_person_data": contact_person_data,
            },
        )
        assert response.status_code == 422

    async def test_update_event_unauthorized(
        self,
        http_client: AsyncClient,
        event_fixture: Event,
        user_fixture: User,
        user_fixture_2: User,
        city_fixture: City,
        specialization_fixture_2: Specialization,
        organisation_fixture: Organisation,
    ) -> None:
        update_data = json.dumps(
            {
                "title": "Updated Creativehub Fest",
                "description": "Update IZI FEST",
                "language": "German",
                "extra_languages": ["English", "French"],
                "event_type": "Exhibition",
                "is_free": True,
                "is_online": False,
                "city_id": city_fixture.id,
                "places": [
                    {
                        "address": "123 Creative St, Cityville",
                        "place_name": "Village",
                    }
                ],
                "online_links": ["https://wwww.creativehub.com/"],
                "start_datetime": "2024-11-15T06:49:19.667Z",
                "end_datetime": "2024-11-25T06:49:19.667Z",
                "registration_end_type": "At event start",
                "reminders": [
                    {"reminder_before_event": 1, "reminder_unit": "minutes"}
                ],
                "specializations_ids": [specialization_fixture_2.id],
                "speakers_uids": [str(user_fixture.uid)],
                "organisations_ids": [organisation_fixture.id],
                "organizers_uids": [str(user_fixture_2.uid)],
                "is_draft": True,
                "is_archived": False,
            }
        )

        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/"
        response = await http_client.patch(
            endpoint,
            data={
                "update_data": update_data,
                "contact_person_data": contact_person_data,
            },
        )
        assert response.status_code == 401, response.text

    async def test_update_event_with_invalid_data(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_fixture: Event,
        user_fixture: User,
        user_fixture_2: User,
        city_fixture: City,
        specialization_fixture_2: Specialization,
        organisation_fixture: Organisation,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)

        update_data = json.dumps(
            {
                "title": "Updated Creativehub Fest",
                "description": "Update IZI FEST",
                "language": "German",
                "extra_languages": ["English", "French"],
                "event_type": 2,
                "is_free": 1,
                "is_online": False,
                "city_id": city_fixture.id,
                "places": [
                    {
                        "address": "123 Creative St, Cityville",
                        "place_name": "Village",
                    }
                ],
                "online_links": ["https://wwww.creativehub.com/"],
                "start_datetime": "2024-11-15T06:49:19.667Z",
                "end_datetime": "2024-11-25T06:49:19.667Z",
                "registration_end_type": "At event start",
                "reminders": [
                    {"reminder_before_event": 1, "reminder_unit": "minutes"}
                ],
                "specializations_ids": [specialization_fixture_2.id],
                "speakers_uids": [str(user_fixture.uid)],
                "organisations_ids": [organisation_fixture.id],
                "organizers_uids": [str(user_fixture_2.uid)],
                "is_draft": True,
                "is_archived": False,
            }
        )

        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": update_data,
                "contact_person_data": contact_person_data,
            },
        )
        assert response.status_code == 422, response.text

    async def test_update_event_with_invalid_reminders(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_fixture: Event,
        user_fixture: User,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)

        update_data = json.dumps(
            {
                "reminders": [
                    {"reminder_before_event": 1, "reminder_unit": "days"}
                ],
                "is_draft": False,
                "is_archived": False,
            }
        )

        contact_person_data = json.dumps(
            {
                "data": [
                    {
                        "contact_person_create_data": {
                            "fullname": "John Doe",
                            "position": "Manager",
                            "phone": "1234567890",
                            "email": "johndoe@example.com",
                            "messengers": [
                                {
                                    "messenger": "VK",
                                    "messenger_username": "johndoevk",
                                }
                            ],
                            "photo_filename": "johndoe.jpg",
                        }
                    }
                ]
            }
        )

        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": update_data,
                "contact_person_data": contact_person_data,
            },
        )
        assert response.status_code == 422

    async def test_attend_event_success(
        self,
        user_fixture: User,
        event_fixture: Event,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/attend/"
        response = await http_client.post(endpoint, headers=user_auth_headers)
        assert response.status_code == 200, response.text

        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/"
        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert response_data["participants_count"] == 2

    async def test_attend_event_not_found(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        non_existent_event_id = 999999999
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{non_existent_event_id}/attend/"
        response = await http_client.post(endpoint, headers=user_auth_headers)
        assert response.status_code == 404, response.text

    async def test_attend_event_already_registered(
        self,
        user_fixture: User,
        event_fixture: Event,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/attend/"
        response = await http_client.post(endpoint, headers=user_auth_headers)
        assert response.status_code == 200

        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/attend/"
        response = await http_client.post(endpoint, headers=user_auth_headers)
        assert response.status_code == 400, response.text

    async def test_cancel_attendance_success(
        self,
        user_fixture: User,
        event_fixture: Event,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        user_auth_headers = await get_auth_headers(user_fixture)

        endpoint_1 = f"{ROOT_ENDPOINT}{event_fixture.id}/attend/"
        response = await http_client.post(
            endpoint_1, headers=user_auth_headers
        )
        assert response.status_code == 200, response.text
        endpoint = f"{ROOT_ENDPOINT}{event_fixture.id}/cancel_attendance/"
        response = await http_client.delete(
            endpoint, headers=user_auth_headers
        )
        assert response.status_code == 200, response.text

    async def test_cancel_attendance_event_not_found(
        self,
        user_fixture: User,
        event_fixture: Event,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        user_auth_headers = await get_auth_headers(user_fixture)

        endpoint_1 = f"{ROOT_ENDPOINT}{event_fixture.id}/attend/"
        response = await http_client.post(
            endpoint_1, headers=user_auth_headers
        )
        assert response.status_code == 200, response.text

        non_existent_event_id = 999999999
        endpoint = f"{ROOT_ENDPOINT}{non_existent_event_id}/cancel_attendance/"
        response = await http_client.delete(
            endpoint, headers=user_auth_headers
        )
        assert response.status_code == 404, response.text

    async def test_cancel_attendance_not_registered(
        self,
        user_fixture: User,
        event_fixture: Event,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.delete(
            f"{ROOT_ENDPOINT}{event_fixture.id}/cancel_attendance/",
            headers=user_auth_headers,
        )
        assert response.status_code == 400, response.text

    async def test_read_events_for_author_success(
        self,
        user_fixture: User,
        event_fixture: Event,
        event_fixture_2: Event,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}author/all/"
        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert len(response_data["objects"]) == 2
        assert response_data["objects"][0]["id"] == event_fixture.id
        assert response_data["objects"][1]["id"] == event_fixture_2.id

    async def test_read_events_for_author_no_events(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}author/all/"
        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert response_data["objects"] == []

    async def test_read_all_event_languages(
        self,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ):
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}languages/all/"
        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert len(response_data["languages"]) > 2

    async def test_read_events_for_author_is_draft(
        self,
        event_fixture_2: Event,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}author/all/"
        response = await http_client.get(
            endpoint, headers=user_auth_headers, params={"is_draft": True}
        )
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert isinstance(response_data["objects"], list)
        assert response_data["objects"][0]["id"] == event_fixture_2.id
        assert response_data["objects"][0]["is_draft"] is True

    async def test_read_events_for_author_is_archived(
        self,
        event_fixture_3: Event,
        user_fixture: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}author/all/"
        response = await http_client.get(
            endpoint, headers=user_auth_headers, params={"is_archived": True}
        )
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert isinstance(response_data["objects"], list)
        assert response_data["objects"][0]["id"] == event_fixture_3.id
        assert response_data["objects"][0]["is_archived"] is True

    async def test_read_events_for_author_is_archived_wrong_user(
        self,
        event_fixture_3: Event,
        user_fixture_2: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}author/all/"
        response = await http_client.get(
            endpoint, headers=user_auth_headers, params={"is_archived": True}
        )
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert isinstance(response_data["objects"], list)
        assert response_data["objects"] == []

    async def test_read_events_count_for_author(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        event_fixture: Event,
        event_fixture_2: Event,
        event_fixture_3: Event,
        user_fixture: User,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}author/all/count/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == {
            "archived_events_count": 1,
            "draft_events_count": 1,
            "published_events_count": 1,
        }

    async def test_read_event_participants(
        self,
        event_fixture: Event,
        user_fixture: User,
        user_fixture_2: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}participants/{event_fixture.id}/"
        response = await http_client.get(endpoint, headers=user_auth_headers)
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert isinstance(response_data["objects"], list)
        assert len(response_data["objects"]) > 0
        assert (
            response_data["objects"][0]["first_name"]
            == user_fixture_2.first_name
        )
        assert response_data["objects"][0]["uid"] == str(user_fixture_2.uid)

    async def test_read_event_participants_with_filter(
        self,
        event_fixture: Event,
        user_fixture: User,
        user_fixture_2: User,
        http_client: AsyncClient,
        get_auth_headers: Callable,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}participants/{event_fixture.id}/"
        response = await http_client.get(
            endpoint, headers=user_auth_headers, params={"search": "another"}
        )
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert isinstance(response_data["objects"], list)
        assert len(response_data["objects"]) > 0
        assert (
            response_data["objects"][0]["first_name"]
            == user_fixture_2.first_name
        )
        assert response_data["objects"][0]["uid"] == str(user_fixture_2.uid)

        response = await http_client.get(
            endpoint, headers=user_auth_headers, params={"search": "exist"}
        )
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert isinstance(response_data["objects"], list)
        assert len(response_data["objects"]) == 0

    async def test_seacrh_event_by_title(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
        event_fixture: Organisation,
    ):
        search_term = event_fixture.title
        endpoint = f"{ROOT_ENDPOINT}?limit=50&skip=0&search={search_term}"
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(endpoint, headers=user_auth_headers)
        response_data = response.json()

        assert response.status_code == 200, response.text
        event_data = response_data["objects"][0]

        assert event_data["title"] == event_fixture.title, response.text

    async def test_seacrh_event_by_description(
        self,
        http_client: AsyncClient,
        user_fixture: User,
        get_auth_headers: Callable,
        event_fixture: Organisation,
    ):
        search_term = event_fixture.description
        endpoint = f"{ROOT_ENDPOINT}?limit=50&skip=0&search={search_term}"
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(endpoint, headers=user_auth_headers)
        response_data = response.json()

        assert response.status_code == 200, response.text
        event_data = response_data["objects"][0]

        assert (
            event_data["description"] == event_fixture.description
        ), response.text
