import uuid

import fastapi
import httpx
import sqlalchemy

from src.config.manager import settings
from src.models.schemas.contact import ContactInResponse, ContactFormInCreate
from src.repository.crud.base import BaseCRUDRepository
from src.models.db.contact import Contact

class ContactCRUDRepository(BaseCRUDRepository):

    async def generate_uuid(self, ip: str):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, ip))
    async def get_user_info(self, request: fastapi.Request):
        ip = request.client.host
        ipregistry_api_key = settings.IPREGISTRY_API_KEY
        url = f"https://api.ipregistry.co/{ip}?key={ipregistry_api_key}"

        stmt = sqlalchemy.select(Contact).filter(Contact.ip == ip)
        result = await self.async_session.execute(stmt)
        contact = result.scalars().first()
        if contact:
            return ContactInResponse(
                calling_code=contact.calling_code,
                country_name=contact.country_name,
                country_code=contact.country_code,
                region_name=contact.region_name,
                city=contact.city,
                uuid=contact.uuid,
            )
        if ip == "127.0.0.1":
            country_name = "Local"
            country_code = "Local"
            region_name = "Local"
            city = "Local"
            uuid = await self.generate_uuid(ip=ip)
            contact = Contact(
                ip=ip,
                calling_code="Local",
                country_name=country_name,
                country_code=country_code,
                region_name=region_name,
                city=city,
                uuid=uuid,
            )
            self.async_session.add(contact)
            await self.async_session.commit()
            return ContactInResponse(
                calling_code="Local",
                country_name=country_name,
                country_code=country_code,
                region_name=region_name,
                city=city,
                uuid=uuid,
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()  # 会抛出异常，如果响应状态不是200
                result = response.json()
                calling_code = result["location"]["country"]["calling_code"]
                country_name = result["location"]["country"]["name"]
                country_code = result["location"]["country"]["code"]
                region_name = result["location"]["region"]["name"]
                city = result["location"]["city"]
                uuid = await self.generate_uuid(ip=ip)
                contact = Contact(
                    ip=ip,
                    calling_code=calling_code,
                    country_name=country_name,
                    country_code=country_code,
                    region_name=region_name,
                    city=city,
                    uuid=uuid,
                )
                self.async_session.add(contact)
                await self.async_session.commit()
                return ContactInResponse(
                    calling_code=calling_code,
                    country_name=country_name,
                    country_code=country_code,
                    region_name=region_name,
                    city=city,
                    uuid=uuid,
                )
        except httpx.HTTPStatusError as e:
            print(f"An error occurred: {e}")
            return ContactInResponse(
                calling_code="Unknown",
                country_name="Unknown",
                country_code="Unknown",
                region_name="Unknown",
                city="Unknown",
                uuid=await self.generate_uuid(ip=ip),
            )
        except httpx.RequestError as e:
            print(f"An error occurred: {e}")
            return ContactInResponse(
                calling_code="Unknown",
                country_name="Unknown",
                country_code="Unknown",
                region_name="Unknown",
                city="Unknown",
                uuid=await self.generate_uuid(ip=ip),
            )

    async def create_contact(self, form: ContactFormInCreate):
        stmt = sqlalchemy.select(Contact).filter(Contact.uuid == form.uuid)
        result = await self.async_session.execute(stmt)
        contact = result.scalars().first()
        contact.name = form.name
        contact.email = form.email
        contact.phone = form.phone
        contact.message = form.message
        contact.calling_code = form.calling_code
        await self.async_session.commit()
        return contact

