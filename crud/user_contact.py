from crud.async_crud import BaseAsyncCRUD
from models import UserContact
from schemas.user.user_contact_info import (
    ContactInfoCreateDB,
    ContactInfoUpdate,
)


class CRUDUserContact(
    BaseAsyncCRUD[UserContact, ContactInfoCreateDB, ContactInfoUpdate]
):
    ...


crud_user_contact = CRUDUserContact(UserContact)
