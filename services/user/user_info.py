from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from crud.link import crud_link
from crud.private_site import crud_private_site
from crud.user import crud_user
from models import User
from schemas.link import LinkCreateDB, LinkUpdateDB
from schemas.private_site import (
    PrivateSiteCreate,
    PrivateSiteCreateDB,
    PrivateSiteUpdate,
)
from schemas.user.user_info import LinkCreateUpdate, UserInfoCreateUpdate
from utilities.queryset import check_found


async def create_update_user_info(
    db: AsyncSession, schema: UserInfoCreateUpdate, user_uid: UUID
) -> User:
    try:
        user = await crud_user.get_by_uid_full(db=db, uid=user_uid)

        await create_or_update_links(db=db, schemas=schema.links, user=user)
        await create_or_update_private_site(
            db=db, schema=schema.private_site, user=user
        )

        contact_info_update_data = schema.contact_info.model_dump()
        if contact_info_update_data:
            user.contact_info = contact_info_update_data

        await db.commit()
        db.expire_all()
        return await crud_user.get_by_uid_full(db=db, uid=user_uid)
    except Exception:
        await db.rollback()
        raise


async def create_or_update_links(
    db: AsyncSession, schemas: List[LinkCreateUpdate], user: User
) -> None:
    if not schemas and user.links:
        await crud_link.remove_bulk(
            db=db, ids=[link.id for link in user.links], commit=False
        )
    elif schemas:
        links_ids, create_schemas, update_schemas = [], [], []
        for link in schemas:
            if link.id:
                links_ids.append(link.id)
                update_schemas.append(LinkUpdateDB(**link.model_dump()))
            else:
                create_schemas.append(
                    LinkCreateDB(
                        **link.model_dump(exclude_unset=True), user_id=user.id
                    )
                )

        found_links = await crud_link.get_multi_by_ids(db=db, ids=links_ids)
        await check_found(found_links, links_ids)
        if create_schemas:
            created_links = await crud_link.create_bulk(
                db=db, create_schemas=create_schemas, commit=False
            )
            links_ids.extend([e.id for e in created_links])
        if update_schemas:
            await crud_link.update_bulk(
                db=db, update_schemas=update_schemas, commit=False
            )
        ids_to_delete = [e.id for e in user.links if e.id not in links_ids]
        await crud_link.remove_bulk(db=db, ids=ids_to_delete, commit=False)


async def create_or_update_private_site(
    db: AsyncSession, schema: PrivateSiteCreate, user: User
) -> None:
    if not schema and user.private_site:
        await crud_private_site.remove(
            db=db, obj_id=user.private_site.id, commit=False
        )
    elif schema:
        if user.private_site:
            update_schema = PrivateSiteUpdate(**schema.model_dump())
            await crud_private_site.update(
                db=db,
                db_obj=user.private_site,
                update_data=update_schema,
                commit=False,
            )
        else:
            create_schema = PrivateSiteCreateDB(
                **schema.model_dump(), user_id=user.id
            )
            await crud_private_site.create(
                db=db, create_schema=create_schema, commit=False
            )
