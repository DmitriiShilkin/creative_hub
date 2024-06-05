import json
import uuid
from io import BytesIO
from typing import Callable

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from constants.education import EducationType
from models import City, Education, User

ROOT_ENDPOINT = "/ch/v1/user-education/"


class TestUserEducationAPI:
    async def test_get_multi(
        self,
        http_client: AsyncSession,
        user_fixture: User,
        user_education_fixture: Education,
    ) -> None:
        endpoint = f"{ROOT_ENDPOINT}{user_fixture.uid}/"
        response = await http_client.get(
            endpoint,
        )
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 1

    async def test_get_multi_invalid_user(
        self,
        http_client: AsyncSession,
    ) -> None:
        endpoint = f"{ROOT_ENDPOINT}{uuid.uuid4()}/"
        response = await http_client.get(
            endpoint,
        )
        assert response.status_code == 404

    async def test_create(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        city_fixture: City,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        create_data = {
            "educations": [
                {
                    "end_year": 1950,
                    "start_month": 1,
                    "is_current": False,
                    "name": "string",
                    "filenames": ["test.txt"],
                    "city_id": city_fixture.id,
                    "department": "string",
                    "start_year": 1950,
                    "type": "Высшее",
                    "end_month": 1,
                }
            ]
        }
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={"create_data": json.dumps(create_data)},
            files={"files": (file.filename, file.file, "text/plain")},
        )
        assert response.status_code == 201

        response_data = response.json()
        assert "Высшее" in response_data[0].values()
        assert response_data[0]["certificates"][0]["file"]

    async def test_create_invalid_city(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        create_data = {
            "educations": [
                {
                    "end_year": 1950,
                    "start_month": 1,
                    "is_current": False,
                    "name": "string",
                    "filenames": ["test.txt"],
                    "city_id": 999,
                    "department": "string",
                    "start_year": 1950,
                    "type": "Высшее",
                    "end_month": 1,
                }
            ]
        }
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={"create_data": json.dumps(create_data)},
            files={"files": (file.filename, file.file, "text/plain")},
        )
        assert response.status_code == 404

    async def test_create_invalid_files(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        city_fixture: City,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        create_data = {
            "educations": [
                {
                    "end_year": 1950,
                    "start_month": 1,
                    "is_current": False,
                    "name": "string",
                    "filenames": ["invalid_name.txt"],
                    "city_id": city_fixture.id,
                    "department": "string",
                    "start_year": 1950,
                    "type": "Высшее",
                    "end_month": 1,
                }
            ]
        }
        response = await http_client.post(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={"create_data": json.dumps(create_data)},
            files={"files": (file.filename, file.file, "text/plain")},
        )
        assert response.status_code == 404

    async def test_update_multi(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        city_fixture: City,
        user_education_fixture: Education,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        update_data = {
            "educations": [
                {
                    "end_year": 1950,
                    "start_month": 1,
                    "is_current": False,
                    "name": "string",
                    "filenames": ["test.txt"],
                    "city_id": city_fixture.id,
                    "department": "string",
                    "start_year": 1950,
                    "type": "Высшее",
                    "end_month": 1,
                    "education_id": user_education_fixture.id,
                }
            ]
        }
        response = await http_client.put(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
            files={"files": (file.filename, file.file, "text/plain")},
        )
        assert response.status_code == 200

        response_data = response.json()
        assert "Высшее" in response_data[0].values()
        assert response_data[0]["certificates"][0]["file"]

    async def test_update_multi_invalid_education(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        city_fixture: City,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        update_data = {
            "educations": [
                {
                    "end_year": 1950,
                    "start_month": 1,
                    "is_current": False,
                    "name": "string",
                    "filenames": ["test.txt"],
                    "city_id": city_fixture.id,
                    "department": "string",
                    "start_year": 1950,
                    "type": "Высшее",
                    "end_month": 1,
                    "education_id": 999,
                }
            ]
        }
        response = await http_client.put(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
            files={"files": (file.filename, file.file, "text/plain")},
        )
        assert response.status_code == 404

    async def test_update_multi_invalid_city(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        user_education_fixture: Education,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        update_data = {
            "educations": [
                {
                    "end_year": 1950,
                    "start_month": 1,
                    "is_current": False,
                    "name": "string",
                    "filenames": ["test.txt"],
                    "city_id": 999,
                    "department": "string",
                    "start_year": 1950,
                    "type": "Высшее",
                    "end_month": 1,
                    "education_id": user_education_fixture.id,
                }
            ]
        }
        response = await http_client.put(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
            files={"files": (file.filename, file.file, "text/plain")},
        )
        assert response.status_code == 404

    async def test_update_multi_invalid_files(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        city_fixture: City,
        user_education_fixture: Education,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        update_data = {
            "educations": [
                {
                    "end_year": 1950,
                    "start_month": 1,
                    "is_current": False,
                    "name": "string",
                    "filenames": ["invalid_name.txt"],
                    "city_id": city_fixture.id,
                    "department": "string",
                    "start_year": 1950,
                    "type": "Высшее",
                    "end_month": 1,
                    "education_id": user_education_fixture.id,
                }
            ]
        }
        response = await http_client.put(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
            files={"files": (file.filename, file.file, "text/plain")},
        )
        assert response.status_code == 404

    async def test_update_multi_invalid_user(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture_2: User,
        city_fixture: City,
        user_education_fixture: Education,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        update_data = {
            "educations": [
                {
                    "end_year": 1950,
                    "start_month": 1,
                    "is_current": False,
                    "name": "string",
                    "filenames": ["test.txt"],
                    "city_id": city_fixture.id,
                    "department": "string",
                    "start_year": 1950,
                    "type": "Высшее",
                    "end_month": 1,
                    "education_id": user_education_fixture.id,
                }
            ]
        }
        response = await http_client.put(
            ROOT_ENDPOINT,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
            files={"files": (file.filename, file.file, "text/plain")},
        )
        assert response.status_code == 403

    async def test_update_certificate_creation_deletion(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        user_education_fixture: Education,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{user_education_fixture.id}/"
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        update_data = {
            "filenames": ["test.txt"],
            "type": EducationType.ADDITIONAL,
        }
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
            files={"files": (file.filename, file.file, "text/plain")},
        )
        assert response.status_code == 200
        response_data = response.json()

        assert EducationType.ADDITIONAL in response_data.values()
        assert response_data["certificates"][0]["file"]

        update_data = {
            "certificates_ids_to_delete": [1],
        }
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["certificates"] == []

    async def test_update_invalid_certificate_deletion(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        user_education_fixture: Education,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{user_education_fixture.id}/"
        update_data = {
            "certificates_ids_to_delete": [1],
        }
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
        )
        assert response.status_code == 404

    async def test_update_invalid_education(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{999}/"
        update_data = {
            "type": EducationType.ADDITIONAL,
        }
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
        )
        assert response.status_code == 404

    async def test_update_invalid_city(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        user_education_fixture: Education,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{user_education_fixture.id}/"
        update_data = {
            "city_id": 999,
        }
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
        )
        assert response.status_code == 404

    async def test_update_invalid_files(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        user_education_fixture: Education,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{user_education_fixture.id}/"
        file = UploadFile(filename="test.txt", file=BytesIO(b"Test content"))
        update_data = {
            "filenames": ["invalid_name.txt"],
        }
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
            files={"files": (file.filename, file.file, "text/plain")},
        )
        assert response.status_code == 404

    async def test_update_invalid_user(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture_2: User,
        user_education_fixture: Education,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}{user_education_fixture.id}/"
        update_data = {
            "type": EducationType.ADDITIONAL,
        }
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
        )
        assert response.status_code == 403

    async def test_update_invalid_date(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        user_education_fixture: Education,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{user_education_fixture.id}/"
        update_data = {
            "end_year": 2020,
            "start_month": 7,
        }
        response = await http_client.patch(
            endpoint,
            headers=user_auth_headers,
            data={"update_data": json.dumps(update_data)},
        )
        assert response.status_code == 409

    async def test_delete(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
        user_education_fixture: Education,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{user_education_fixture.id}/"
        response = await http_client.delete(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 204

    async def test_delete_invalid_education(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture: User,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture)
        endpoint = f"{ROOT_ENDPOINT}{999}/"
        response = await http_client.delete(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 404

    async def test_delete_invalid_user(
        self,
        http_client: AsyncSession,
        get_auth_headers: Callable,
        user_fixture_2: User,
        user_education_fixture: Education,
    ) -> None:
        user_auth_headers = await get_auth_headers(user_fixture_2)
        endpoint = f"{ROOT_ENDPOINT}{user_education_fixture.id}/"
        response = await http_client.delete(
            endpoint,
            headers=user_auth_headers,
        )
        assert response.status_code == 403
