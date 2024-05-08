import datetime
import typing

import sqlalchemy
from fastapi import HTTPException
from sqlalchemy.sql import functions as sqlalchemy_functions
import httpx
import re
import random
import string

from src.config.manager import settings
from src.models.db.account import Account, Referal, CustomerService
from src.models.db.task import Task, TaskCategory
from src.models.db.wallet import Wallet
from src.models.schemas.account import AccountInCreate, AccountInLogin, AccountInUpdate
from src.models.schemas.account import IPCheckInResponse
from src.models.schemas.wallet import WalletInCreate
from src.repository.crud.base import BaseCRUDRepository
from src.securities.hashing.password import pwd_generator
from src.securities.verifications.credentials import credential_verifier
from src.utilities.exceptions.database import EntityAlreadyExists, EntityDoesNotExist
from src.utilities.exceptions.password import PasswordDoesNotMatch


class AccountCRUDRepository(BaseCRUDRepository):
    async def create_account(self, account_create: AccountInCreate,request) -> typing.Tuple[Account, Wallet]:
        new_account = Account(username=account_create.username, email=account_create.email, is_logged_in=True, registration_ip=request.client.host)

        new_account.set_hash_salt(hash_salt=pwd_generator.generate_salt)
        new_account.set_hashed_password(
            hashed_password=pwd_generator.generate_hashed_password(
                hash_salt=new_account.hash_salt, new_password=account_create.password
            )
        )

        self.async_session.add(instance=new_account)
        await self.async_session.flush()
        new_account, new_wallet= await self.initialize_account(account=new_account)
        return new_account, new_wallet

    async def create_account_by_admin(self, account_create: AccountInCreate,request) -> Account:
        new_account = Account(username=account_create.username, email=account_create.email, is_logged_in=True, registration_ip=request.client.host, is_test_account=True)

        new_account.set_hash_salt(hash_salt=pwd_generator.generate_salt)
        new_account.set_hashed_password(
            hashed_password=pwd_generator.generate_hashed_password(
                hash_salt=new_account.hash_salt, new_password=account_create.password
            )
        )

        self.async_session.add(instance=new_account)
        await self.async_session.flush()
        new_account, new_wallet= await self.initialize_account(account=new_account)
        return new_account, new_wallet


    async def read_accounts(self) -> typing.Sequence[Account]:
        stmt = sqlalchemy.select(Account)
        query = await self.async_session.execute(statement=stmt)
        return query.scalars().all()

    async def read_account_by_id(self, id: int) -> Account:
        stmt = sqlalchemy.select(Account).options(sqlalchemy.orm.joinedload(Account.wallet), sqlalchemy.orm.joinedload(Account.tasks)).where(Account.id == id)
        query = await self.async_session.execute(statement=stmt)

        if not query:
            raise EntityDoesNotExist("Account with id `{id}` does not exist!")

        return query.scalar()  # type: ignore

    async def read_account_by_username(self, username: str, request) -> Account:
        stmt = sqlalchemy.select(Account).options(sqlalchemy.orm.joinedload(Account.wallet), sqlalchemy.orm.joinedload(Account.tasks)).where(Account.username == username)
        query = await self.async_session.execute(statement=stmt)

        if not query:
            raise EntityDoesNotExist(f"Account with username `{username}` does not exist!")

        db_account = query.scalar()  # type: ignore
        db_account.current_ip = request.client.host
        db_account.is_logged_in = True
        ip_check = await self.is_ip_proxy(ip=db_account.current_ip)
        db_account.is_proxy = ip_check.is_proxy
        db_account.ip_location = ip_check.ip_location
        db_account.updated_at = datetime.datetime.now()
        db_account.user_agent = request.headers['user-agent']
        await self.async_session.commit()
        await self.async_session.refresh(instance=db_account)
        return db_account

    async def read_account_by_email(self, email: str) -> Account:
        stmt = sqlalchemy.select(Account).options(sqlalchemy.orm.selectinload(Account.wallet)).where(Account.email == email)
        query = await self.async_session.execute(statement=stmt)

        if not query:
            raise EntityDoesNotExist(f"Account with email `{email}` does not exist!")

        return query.scalar()  # type: ignore

    async def read_user_by_password_authentication(self, account_login: AccountInLogin, request) -> Account:
        stmt = sqlalchemy.select(Account).where(
            sqlalchemy.or_(Account.username == account_login.username_or_email, Account.email == account_login.username_or_email)
        )
        query = await self.async_session.execute(statement=stmt)
        db_account = query.scalar()

        if not db_account:
            raise HTTPException(status_code=400, detail="Account does not exist!")  # type: ignore

        if not pwd_generator.is_password_authenticated(hash_salt=db_account.hash_salt, password=account_login.password, hashed_password=db_account.hashed_password):  # type: ignore
            raise HTTPException(status_code=400, detail="Password does not match!")  # type: ignore

        db_account.current_ip = request.client.host
        db_account.is_logged_in = True
        ip_check = await self.is_ip_proxy(ip=db_account.current_ip)
        db_account.is_proxy = ip_check.is_proxy
        db_account.ip_location = ip_check.ip_location
        await self.async_session.commit()
        await self.async_session.refresh(instance=db_account)

        return db_account  # type: ignore

    async def update_account_by_id(self, id: int, account_update: AccountInUpdate) -> Account:
        new_account_data = account_update.dict()

        select_stmt = sqlalchemy.select(Account).where(Account.id == id)
        query = await self.async_session.execute(statement=select_stmt)
        update_account = query.scalar()

        if not update_account:
            raise EntityDoesNotExist(f"Account with id `{id}` does not exist!")  # type: ignore

        update_stmt = sqlalchemy.update(table=Account).where(Account.id == update_account.id).values(updated_at=sqlalchemy_functions.now())  # type: ignore

        if new_account_data["username"] and new_account_data["username"] != update_account.username:
            await self.is_username_taken(username=new_account_data["username"])
            update_stmt = update_stmt.values(username=new_account_data["username"])

        if new_account_data["email"] and new_account_data["email"] != update_account.email:
            await self.is_email_taken(email=new_account_data["email"])
            update_stmt = update_stmt.values(email=new_account_data["email"])

        if new_account_data["password"]:
            update_account.set_hash_salt(hash_salt=pwd_generator.generate_salt)  # type: ignore
            update_account.set_hashed_password(hashed_password=pwd_generator.generate_hashed_password(hash_salt=update_account.hash_salt, new_password=new_account_data["password"]))  # type: ignore

        if new_account_data["profile_image"]:
            update_stmt = update_stmt.values(profile_image=new_account_data["profile_image"])

        await self.async_session.execute(statement=update_stmt)
        await self.async_session.commit()
        await self.async_session.refresh(instance=update_account)

        return update_account  # type: ignore

    async def delete_account_by_id(self, id: int) -> str:
        select_stmt = sqlalchemy.select(Account).where(Account.id == id)
        query = await self.async_session.execute(statement=select_stmt)
        delete_account = query.scalar()

        if not delete_account:
            raise EntityDoesNotExist(f"Account with id `{id}` does not exist!")  # type: ignore

        stmt = sqlalchemy.delete(table=Account).where(Account.id == delete_account.id)

        await self.async_session.execute(statement=stmt)
        await self.async_session.commit()

        return f"Account with id '{id}' is successfully deleted!"

    async def is_username_taken(self, username: str) -> bool:
        username_stmt = sqlalchemy.select(Account.username).select_from(Account).where(Account.username == username)
        username_query = await self.async_session.execute(username_stmt)
        db_username = username_query.scalar()

        if not credential_verifier.is_username_available(username=db_username):
            raise EntityAlreadyExists(f"The username `{username}` is already taken!")  # type: ignore

        return True

    async def is_email_taken(self, email: str) -> bool:
        email_stmt = sqlalchemy.select(Account.email).select_from(Account).where(Account.email == email)
        email_query = await self.async_session.execute(email_stmt)
        db_email = email_query.scalar()

        if not credential_verifier.is_email_available(email=db_email):
            raise EntityAlreadyExists(f"The email `{email}` is already registered!")  # type: ignore

        return True

    async def initialize_account(self,account: Account):
        new_wallet = Wallet(account_id=account.id)
        self.async_session.add(instance=new_wallet)
        stmp = sqlalchemy.select(TaskCategory).where(TaskCategory.access_level == 1)
        query = await self.async_session.execute(statement=stmp)
        task_categories = query.scalars().all()
        tasks = []
        for task_category in task_categories:
            db_task = Task(
                task_category_id=task_category.id,
                account_id=account.id,
            )
            self.async_session.add(instance=db_task)
            tasks.append(db_task)
        await self.async_session.commit()
        await self.async_session.refresh(instance=account)
        await self.async_session.refresh(instance=new_wallet)
        return account, new_wallet

    async def is_ip_proxy(self, ip: str) -> IPCheckInResponse:
        ipregistry_api_key = settings.IPREGISTRY_API_KEY
        url = f"https://api.ipregistry.co/{ip}?key={ipregistry_api_key}"
        if ip == "127.0.0.1":
            return IPCheckInResponse(ip=ip, is_proxy=False, ip_location="Localhost")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()  # 会抛出异常，如果响应状态不是200
                result = response.json()

            # Simplify proxy check
            is_proxy = any(result.get('security', {}).values())

            # Improve location extraction
            location_data = result.get('location', {})
            country = location_data.get('country', {}).get('name', "Unknown")
            region = location_data.get('region', {}).get('name', "Unknown")
            city = location_data.get('city', "Unknown")
            ip_location = f"{country}, {region}, {city}"

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Error retrieving IP information")
        except KeyError:
            raise ValueError("Malformed response received from IP registry API")

        return IPCheckInResponse(ip=ip, is_proxy=is_proxy, ip_location=ip_location)

    async def verify_recapcha(self, recaptcha: str) -> bool:
        secret_key = "6LeiQ7YpAAAAAAJHyDtBA1-tiUyAM7QSI6KVGigo"
        url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {
            'secret': secret_key,
            'response': recaptcha
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload)
            result = response.json()
        if not result['success']:
            raise Exception("Recaptcha verification failed")
        return True

    async def read_admin_account(self, username: str) -> Account:
        stmt = sqlalchemy.select(Account).where(Account.username == username, Account.is_admin == True)
        query = await self.async_session.execute(statement=stmt)
        db_account = query.scalar()
        return db_account

    async def create_referer(self, user: Account):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        referal = Referal(referal_code=code)
        self.async_session.add(instance=referal)
        await self.async_session.commit()
        await self.async_session.refresh(instance=referal)
        return referal

    async def is_referral_code_valid(self, referral_code: str) -> bool:
        stmt = sqlalchemy.select(Referal).where(Referal.referal_code == referral_code)
        query = await self.async_session.execute(statement=stmt)
        db_referal = query.scalar()

        if not db_referal:
            raise HTTPException(status_code=400, detail="Invalid referral code!")

    async def read_customer_service(self):
        stmt = sqlalchemy.select(CustomerService)
        query = await self.async_session.execute(statement=stmt)
        db_customer_service = query.scalar()
        return db_customer_service

    async def update_customer_service(self, whatsapp_url):
        stmt = sqlalchemy.select(CustomerService)
        query = await self.async_session.execute(statement=stmt)
        customer_service = query.scalar()
        customer_service.whatsapp_url = whatsapp_url
        await self.async_session.commit()
        await self.async_session.refresh(instance=customer_service)
        return customer_service.whatsapp_url

