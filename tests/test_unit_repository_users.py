from datetime import date, datetime
import unittest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users_db_sqlalchemy import generics

from src.models.models import Role, User
from src.schemas.user import UserChangeRole, UserSchema, UserUpdateSchema
from src.repository.users import (
    get_all_users,
    get_user_by_username,
    get_info_by_username,
    get_user_by_email,
    create_user,
    update_user,
    delete_user,
    change_user_role,
    update_password,
    update_token,
    update_avatar_url,
    confirmed_email,    
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(
            id="2380f815-f526-4017-a1df-f69ab48b86f9",
            username="test_user",
            email="test@test.com",
            password="qwerty",
            role="admin",
            confirmed=True,
        )

    async def test_get_all_users(self):
        contacts = [User(), User(), User()]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_all_users(limit=10, offset=0, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_user_by_username(self):
        contact = [
            User(
                name="Bond", username="Bill", email="bill@microsoft.com", confirmed=True
            )
        ]
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_user_by_username(username="Bill", db=self.session)
        self.assertEqual(result, contact)
        
    async def test_get_info_by_username(self):
        contact = User(
                name="Bond", username="Bill", email="bill@microsoft.com", confirmed=True)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        mocked_contact.scalar.return_value = 3
        self.session.execute.return_value = mocked_contact
        result, num = await get_info_by_username(username="Bill", db=self.session)
        self.assertEqual(result, contact)
        self.assertEqual(num, 3)
        
    async def test_get_info_by_username_not_found(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = None
        mocked_contact.scalar.return_value = None
        self.session.execute.return_value = mocked_contact
        result, num = await get_info_by_username(username="Urri", db=self.session)
        self.assertIsNone(result, None)
        self.assertIsNone(num, None)

    async def test_get_user_by_email(self):
        contact = [
            User(
                id="2380f815-f526-4017-a1df-f69ab48b86f9",
                username="Steave",
                email="steave@apple.com",
            )
        ]
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_user_by_email(email="steave@apple.com", db=self.session)
        self.assertEqual(result, contact)

    async def test_get_user_by_email_not_found(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_contact
        result = await get_user_by_email(email="steave@apple.com", db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserSchema(
            name="Bond", username="Bill", email="bill@microsoft.com", password="123456"
        )
        contact = [
            User(
                name="Bond",
                username="Bill",
                email="bill@microsoft.com",
                password="123456",
            )
        ]
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await create_user(body=body, db=self.session)
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)

    async def test_update_user(self):
        body = UserUpdateSchema(
            name="Bond",
            username="Bill",
            email="bill@microsoft.com",
            created_at=datetime.now(),
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = User(
            id="2380f815-f526-4017-a1df-f69ab48b86f9",
            username="Bill",
            email="bill@microsoft.com",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.session.execute.return_value = mocked_contact
        result = await update_user(
            user_id="2380f815-f526-4017-a1df-f69ab48b86f9",
            body=body,
            db=self.session,
            current_user=self.user,
        )
        self.session.execute.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        


    async def test_delete_user(self):
        contact = User(id="c919f556-5faf-4293-bea1-a37f8d3bab36", username='bill', email='bill@test.com', role = "user")
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await delete_user(user_id="c919f556-5faf-4293-bea1-a37f8d3bab36", db = self.session, current_user=contact)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(result, contact)

    async def test_change_user_role(self):
        body = UserChangeRole(role="moderator", banned=True, updated_at=datetime.now())
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = body
        self.session.execute.return_value = mocked_contact
        result = await change_user_role(
            user_id="2380f815-f526-4017-a1df-f69ab48b86f9",
            body=body,
            db=self.session,
            current_user=self.user,
        )
        self.session.execute.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(result.role, body.role)
        self.assertEqual(result.banned, body.banned)
        
    async def test_change_user_role_not_admin(self):
        body = UserChangeRole(role="user", banned=True, updated_at=datetime.now())
        res = UserChangeRole(role="user", banned=False, updated_at=datetime.now())
        user = User(id="c919f556-5faf-4293-bea1-a37f8d3bab36", username='bill', email='bill@test.com', role = "moderator")
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = res
        self.session.execute.return_value = mocked_contact
        result = await change_user_role(
            user_id="2380f815-f526-4017-a1df-f69ab48b86f9",
            body=body,
            db=self.session,
            current_user=user,
        )
        self.session.execute.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(result.role, body.role)
        self.assertNotEqual(result.banned, body.banned)
        self.assertEqual(result.banned, res.banned)
        
    async def test_update_password(self):
        user=self.user
        password = "XXXXXX"
        result = await update_password(
            user=self.user,
            password=password,
            db=self.session,
        )
        self.session.commit.assert_called_once()
        self.assertEqual(user.password, password)
        
    async def test_update_token(self):
        user=self.user
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGdtYWlsLmNvbSIsImlhdCI6MTcxMTk5MTA0NSwiZXhwIjoxNzEyNTk1ODQ1LCJzY29wZSI6InJlZnJlc2hfdG9rZW4ifQ.OMe1FmxnDWvMLVF3EPXNQ1lxhvdLwm2lMBeiwp-VVeo"
        result = await update_token(
            user=self.user,
            token=token,
            db=self.session,
        )
        self.session.commit.assert_called_once()
        self.assertEqual(user.refresh_token, token)
        
    async def test_update_avatar_url(self):
        url="https://www.gravatar.com/avatar/8404dcfdae631dca53b7baebf3e1c21c"
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = User(
            id="2380f815-f526-4017-a1df-f69ab48b86f9",
            username="Bill",
            email="bill@microsoft.com",
            avatar=""  
        )
        self.session.execute.return_value = mocked_contact
        result = await update_avatar_url(
            email="bill@microsoft.com",
            url="https://www.gravatar.com/avatar/8404dcfdae631dca53b7baebf3e1c21c",
            db=self.session
        )
        self.session.commit.assert_called_once()
        self.assertEqual(result.avatar, url)
        
    async def test_confirmed_email(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = User(
            id="2380f815-f526-4017-a1df-f69ab48b86f9",
            username="Bill",
            email="bill@microsoft.com",
            confirmed = True  
        )
        self.session.execute.return_value = mocked_contact
        await confirmed_email(
            email="bill@microsoft.com",
            db=self.session,
        )
        self.session.commit.assert_called_once()
        self.assertTrue(User.confirmed)
        


if __name__ == "__main__":
    unittest.main()
