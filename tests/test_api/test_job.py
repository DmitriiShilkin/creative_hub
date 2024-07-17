import json
from datetime import datetime, UTC
from io import BytesIO
from typing import Callable

from fastapi import UploadFile
from httpx import AsyncClient

from models import (
    City,
    ContactPerson,
    Job,
    Proposal,
    Specialization,
    User,
    Favorite,
)

ROOT_ENDPOINT = "/ch/v1/job/"


class TestJob:
    async def test_read_jobs(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        response = await http_client.get(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, dict), response_data
        assert len(response_data["objects"]) == 1, response_data
        assert response_data["total"] == 1
        for job in response_data["objects"]:
            assert job["is_favorite"] is False
        for job in response_data["objects"]:
            assert job["is_applied"] is False

    async def test_read_jobs_by_specialist(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture_2: User,
        job_fixture: Job,
        proposal_fixture: Proposal,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        response = await http_client.get(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert len(response_data["objects"]) == 1, response_data
        assert (
            job_fixture.id == response_data["objects"][0]["id"]
        ), response_data
        assert (
            proposal_fixture.id
            == response_data["objects"][0]["proposals"][0]["id"]
        )

    async def test_read_jobs_with_favorite_filter(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture_2: User,
        job_fixture: Job,
        job_favorites_list_fixture: Favorite,
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
            job_fixture.id == response_data["objects"][0]["id"]
        ), response_data
        assert response_data["objects"][0]["is_favorite"] is True

    async def test_read_authors_jobs(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture_2: User,
        user_fixture: User,
        job_fixture: Job,
        job_favorites_list_fixture: Favorite,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}author/{user_fixture.uid}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert len(response_data["objects"]) == 1
        assert response_data["objects"][0]["is_favorite"] is True

    async def test_read_authors_jobs_with_favorite_filter(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        user_fixture_2: User,
        job_fixture: Job,
        job_favorites_list_fixture: Favorite,
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
            job_fixture.id == response_data["objects"][0]["id"]
        ), response_data
        assert response_data["objects"][0]["is_favorite"] is True

    async def test_read_job(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{job_fixture.id}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert job_fixture.name in response_data.values()
        assert job_fixture.id == response_data["id"]

    async def test_read_favorite_job_by_specialist(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture_2: User,
        job_fixture: Job,
        job_favorites_list_fixture: Favorite,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}{job_fixture.id}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["is_favorite"] is True
        assert response_data["name"] == job_fixture.name
        assert response_data["id"] == job_fixture.id

    async def test_read_job_with_proposal_by_specialist(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture_2: User,
        job_fixture: Job,
        proposal_fixture: Proposal,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}{job_fixture.id}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == job_fixture.name
        assert response_data["id"] == job_fixture.id
        assert response_data["is_applied"] is True
        assert response_data["proposals"][0]["id"] == proposal_fixture.id

    async def test_read_job_is_archived_by_specialist(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture_2: User,
        job_fixture_2: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}{job_fixture_2.id}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert job_fixture_2.is_archived is True
        assert job_fixture_2.name in response_data.values()
        assert job_fixture_2.id == response_data["id"]

    async def test_read_job_by_specialist(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture_2: User,
        job_fixture: Job,
        proposal_fixture: Proposal,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}{job_fixture.id}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert job_fixture.name in response_data.values()
        assert job_fixture.id == response_data["id"]
        assert proposal_fixture.id == response_data["proposals"][0]["id"]
        assert proposal_fixture.text == response_data["proposals"][0]["text"]

    async def test_read_jobs_by_author(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}author/all/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, dict)
        assert len(response_data["objects"]) == 1
        assert response_data["objects"][0]["name"] == job_fixture.name
        assert response_data["objects"][0]["id"] == job_fixture.id

        response = await http_client.get(
            endpoint, headers=user_auth_headers, params={"is_draft": True}
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["objects"] == []

    async def test_read_jobs_with_proposals_by_specialist(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture_2: User,
        job_fixture: Job,
        proposal_fixture: Proposal,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}applied/all/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["objects"]) == 1
        assert response_data["objects"][0]["id"] == job_fixture.id
        assert (
            response_data["objects"][0]["proposals"][0]["id"]
            == proposal_fixture.id
        )
        assert response_data["objects"][0]["is_applied"] is True

    async def test_read_jobs_without_proposals_by_specialist(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture: Job,
        proposal_fixture: Proposal,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}applied/all/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["objects"]) == 0

    async def test_read_jobs_count_for_author(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        job_fixture: Job,
        job_fixture_2: Job,
        job_fixture_3: Job,
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
            "archived_jobs_count": 1,
            "draft_jobs_count": 1,
            "published_jobs_count": 1,
        }

    async def test_create(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        user_fixture_2: User,
        city_fixture: City,
        specialization_fixture: Specialization,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        person_file = UploadFile(filename="photo.txt", file=BytesIO(b"Photo"))
        create_data = {
            "accepted_languages": ["ru"],
            "specialization_ids": [specialization_fixture.id],
            "payment_per": "hour",
            "budget": 1,
            "for_verified_users": False,
            "name": "string",
            "is_draft": False,
            "is_negotiable_price": False,
            "city_id": city_fixture.id,
            "currency": "rub",
            "adult_content": False,
            "deadline": "2024-05-28T17:04:55.950Z",
            "is_remote": False,
            "author_uid": str(user_fixture.uid),
            "description": "",
            "coauthors_uids": [str(user_fixture_2.uid)],
        }
        contact_person_data = [
            {
                "contact_person_create_data": {
                    "fullname": "string",
                    "position": "string",
                    "phone": "string",
                    "email": "user@example.com",
                    "messengers": [
                        {"messenger": "VK", "messenger_username": "string"}
                    ],
                    "photo_filename": person_file.filename,
                }
            },
        ]
        contact_person_data = {"data": contact_person_data}
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={
                "create_data": json.dumps(create_data),
                "contact_person_data": json.dumps(contact_person_data),
            },
            files={
                "files": (file.filename, file.file, "text/plain"),
                "contact_person_files": (
                    person_file.filename,
                    person_file.file,
                    "text/plain",
                ),
            },
        )
        assert response.status_code == 201, response.text

        response_data = response.json()
        assert create_data["name"] == response_data["name"]
        assert len(response_data["files"]) > 0
        assert len(response_data["contact_persons"]) == 1
        assert (
            datetime.now(tz=UTC).strftime("%Y-%m-%d")
            in response_data["published_at"]
        )

    async def test_create_job_draft_without_author_uid(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        city_fixture: City,
        contact_person_job_fixture: ContactPerson,
        specialization_fixture: Specialization,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        create_data = {
            "accepted_languages": ["ru"],
            "specialization_ids": [specialization_fixture.id],
            "payment_per": "hour",
            "budget": 1,
            "for_verified_users": False,
            "name": "string",
            "is_draft": True,
            "is_negotiable_price": False,
            "city_id": city_fixture.id,
            "currency": "rub",
            "adult_content": False,
            "deadline": "2024-05-28T17:04:55.950Z",
            "is_remote": False,
            "description": "",
        }
        contact_person_data = [
            {"contact_person_id": contact_person_job_fixture.id}
        ]
        contact_person_data = {"data": contact_person_data}
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={
                "create_data": json.dumps(create_data),
                "contact_person_data": json.dumps(contact_person_data),
            },
            files={"files": (file.filename, file.file, "text/plain")},
        )
        assert response.status_code == 201, response.text

        response_data = response.json()
        assert response_data["author"]["uid"] == str(user_fixture.uid)
        assert create_data["name"] == response_data["name"]

    async def test_update(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        user_fixture_2: User,
        specialization_fixture: Specialization,
        job_fixture: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        person_file = UploadFile(filename="photo.txt", file=BytesIO(b"Photo"))
        update_data = {
            "accepted_languages": ["ru"],
            "specialization_ids": [specialization_fixture.id],
            "files_ids_to_delete": [],
            "payment_per": "hour",
            "budget": 1,
            "for_verified_users": False,
            "name": "New name",
            "is_draft": True,
            "is_negotiable_price": False,
            "currency": "rub",
            "adult_content": False,
            "deadline": "2024-05-28T17:04:55.950Z",
            "is_remote": True,
            "author_uid": str(user_fixture.uid),
            "description": "",
            "coauthors_uids": [str(user_fixture_2.uid)],
        }
        contact_person_data = [
            {
                "contact_person_create_data": {
                    "fullname": "string",
                    "position": "string",
                    "phone": "string",
                    "email": "user@example.com",
                    "messengers": [
                        {"messenger": "VK", "messenger_username": "string"}
                    ],
                    "photo_filename": person_file.filename,
                }
            },
        ]
        contact_person_data = {"data": contact_person_data}
        endpoint = f"{ROOT_ENDPOINT}{job_fixture.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": json.dumps(update_data),
                "contact_person_data": json.dumps(contact_person_data),
            },
            files={
                "files": (file.filename, file.file, "text/plain"),
                "contact_person_files": (
                    person_file.filename,
                    person_file.file,
                    "text/plain",
                ),
            },
        )
        assert response.status_code == 200, response.text

        response_data = response.json()
        assert update_data["name"] == response_data["name"]
        assert len(response_data["files"]) > 0
        assert len(response_data["contact_persons"]) == 1

    async def test_update_with_is_draft(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture_2: Job,
        contact_person_job_fixture: ContactPerson,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        update_data = {"is_draft": False}
        contact_person_data = [
            {"contact_person_id": contact_person_job_fixture.id}
        ]
        contact_person_data = {"data": contact_person_data}
        endpoint = f"{ROOT_ENDPOINT}{job_fixture_2.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": json.dumps(update_data),
                "contact_person_data": json.dumps(contact_person_data),
            },
        )
        assert response.status_code == 200, response.text

        response_data = response.json()
        assert len(response_data["contact_persons"]) == 1
        assert response_data["is_draft"] is False

    async def test_update_and_publish_job(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture_2: Job,
        contact_person_job_fixture: ContactPerson,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        update_data = {
            "name": "new name",
            "description": "new description",
            "is_draft": False,
            "is_archived": False,
        }
        contact_person_data = [
            {"contact_person_id": contact_person_job_fixture.id}
        ]
        contact_person_data = {"data": contact_person_data}
        endpoint = f"{ROOT_ENDPOINT}{job_fixture_2.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": json.dumps(update_data),
                "contact_person_data": json.dumps(contact_person_data),
            },
        )
        assert response.status_code == 200, response.text

        response_data = response.json()
        assert len(response_data["contact_persons"]) == 1
        assert response_data["is_draft"] is False
        assert response_data["is_archived"] is False
        assert (
            datetime.now(tz=UTC).strftime("%Y-%m-%d")
            in response_data["published_at"]
        )

    async def test_update_with_null_values(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture: Job,
        contact_person_job_fixture: ContactPerson,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        update_data = {"budget": None, "payment_per": None, "currency": None}
        contact_person_data = [
            {"contact_person_id": contact_person_job_fixture.id}
        ]
        contact_person_data = {"data": contact_person_data}
        endpoint = f"{ROOT_ENDPOINT}{job_fixture.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": json.dumps(update_data),
                "contact_person_data": json.dumps(contact_person_data),
            },
        )
        assert response.status_code == 200, response.text

        response_data = response.json()
        assert len(response_data["contact_persons"]) == 1
        assert response_data["budget"] is None
        assert response_data["payment_per"] is None
        assert response_data["currency"] is None

    async def test_update_job_with_invalid_accepted_languages(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture_2: Job,
        contact_person_job_fixture: ContactPerson,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        update_data = {"accepted_languages": [], "is_draft": False}
        contact_person_data = [
            {"contact_person_id": contact_person_job_fixture.id}
        ]
        contact_person_data = {"data": contact_person_data}
        endpoint = f"{ROOT_ENDPOINT}{job_fixture_2.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": json.dumps(update_data),
                "contact_person_data": json.dumps(contact_person_data),
            },
        )
        assert response.status_code == 409

    async def test_update_job_with_invalid_specialization_ids(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture_2: Job,
        contact_person_job_fixture: ContactPerson,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        update_data = {"specialization_ids": [], "is_draft": False}
        contact_person_data = [
            {"contact_person_id": contact_person_job_fixture.id}
        ]
        contact_person_data = {"data": contact_person_data}
        endpoint = f"{ROOT_ENDPOINT}{job_fixture_2.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={
                "update_data": json.dumps(update_data),
                "contact_person_data": json.dumps(contact_person_data),
            },
        )
        assert response.status_code == 409

    async def test_publish_job(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture_2: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}publish/{job_fixture_2.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert response_data["is_archived"] is False
        assert response_data["is_draft"] is False
        assert (
            datetime.now(tz=UTC).strftime("%Y-%m-%d")
            in response_data["published_at"]
        )

    async def test_publish_job_already_published(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}publish/{job_fixture.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 409

    async def test_publish_job_unauthorized(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture_2: User,
        job_fixture: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}publish/{job_fixture.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 403

    async def test_unpublish_job(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}unpublish/{job_fixture.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200, response.text
        response_data = response.json()
        assert response_data["is_archived"] is True

    async def test_unpublish_job_already_unpublished(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture_2: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}unpublish/{job_fixture_2.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 409

    async def test_unpublish_job_unauthorized(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture_2: User,
        job_fixture: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}unpublish/{job_fixture.id}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 403

    async def test_publish_job_with_invalid_id(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}publish/{job_fixture.id + 2}/"
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 404

    async def test_delete_job(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{job_fixture.id}/"
        response = await http_client.delete(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 204

    async def test_copy_job(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}copy/{job_fixture.id}/"
        response = await http_client.post(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 201, response.text

    async def test_read_job_views_count(
        self,
        http_client: AsyncClient,
        get_auth_headers: Callable,
        user_fixture: User,
        job_fixture: Job,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{job_fixture.id}/"
        response = await http_client.get(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 200, response.text
        response_2 = await http_client.get(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
        )
        response_data_2 = response_2.json()
        initial_views = response_data_2["objects"][0]["views"]
        assert initial_views == 1

        response_3 = await http_client.get(
            endpoint,
        )
        assert response_3.status_code == 200, response_3.text
        response_4 = await http_client.get(
            ROOT_ENDPOINT,
        )
        response_data_4 = response_4.json()
        seconds_views = response_data_4["objects"][0]["views"]
        assert seconds_views == initial_views + 1
