from fastapi import Request, Depends, HTTPException, status

from src.models.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, request: Request, user: User = Depends(auth_service.get_current_user)
    ):
        """
        The __call__ function is a decorator that takes in the request and user as arguments.
        It then checks if the user's role is allowed to access this endpoint, and raises an exception if not.

        :param self: Access the class attributes
        :param request: Request: Pass the request object to the function
        :param user: User: Get the user object from the auth_service
        :return: A function that takes a request and user as arguments
        :doc-author: Trelent
        """
        if user:
            print(user)
            # print(user.role, self.allowed_roles)
            if user.role not in self.allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
                )
