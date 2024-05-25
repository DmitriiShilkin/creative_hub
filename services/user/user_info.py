from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from crud.link import crud_link
from crud.social_network import crud_social_network
from crud.user import crud_user
from crud.user_contact import crud_user_contact
from models import User
from schemas.link import LinkCreateDB, LinkUpdateDB
from schemas.social_network import SocialNetworkCreateDB, SocialNetworkUpdateDB
from schemas.user.user_info import (
    LinkCreateUpdate,
    SocialNetworksCreateUpdate,
    UserInfoCreateUpdate,
)
from utilities.queryset import check_found


async def create_update_user_info(
    db: AsyncSession, schema: UserInfoCreateUpdate, user_uid: UUID
) -> User:
    try:
        user = await crud_user.get_by_uid_full(db=db, uid=user_uid)

        await create_or_update_links(db=db, schemas=schema.links, user=user)
        await create_or_update_networks(
            db=db, schemas=schema.networks, user=user
        )
        await crud_user_contact.update(
            db=db,
            db_obj=user.contact_info,
            update_data=schema.contact_info.model_dump(),
            commit=False,
        )
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as ex:
        await db.rollback()
        raise ex


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


async def create_or_update_networks(
    db: AsyncSession, schemas: List[SocialNetworksCreateUpdate], user: User
) -> None:
    if not schemas and user.social_networks:
        await crud_social_network.remove_bulk(
            db=db, ids=[n.id for n in user.social_networks], commit=False
        )
    elif schemas:
        networks_ids, create_schemas, update_schemas = [], [], []
        for network in schemas:
            if network.id:
                networks_ids.append(network.id)
                update_schemas.append(
                    SocialNetworkUpdateDB(**network.model_dump())
                )
            else:
                create_schemas.append(
                    SocialNetworkCreateDB(
                        **network.model_dump(exclude_unset=True),
                        user_id=user.id
                    )
                )
        found_networks = await crud_social_network.get_multi_by_ids(
            db=db, ids=networks_ids
        )
        await check_found(found_networks, networks_ids)
        if create_schemas:
            created_networks = await crud_social_network.create_bulk(
                db=db, create_schemas=create_schemas, commit=False
            )
            networks_ids.extend([e.id for e in created_networks])
        if update_schemas:
            await crud_social_network.update_bulk(
                db=db, update_schemas=update_schemas, commit=False
            )
        ids_to_delete = [
            e.id for e in user.social_networks if e.id not in networks_ids
        ]
        await crud_social_network.remove_bulk(
            db=db, ids=ids_to_delete, commit=False
        )
