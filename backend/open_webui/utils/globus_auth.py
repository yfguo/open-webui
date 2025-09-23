import time
import globus_sdk
from pydantic import BaseModel
from typing import Optional, List
from dataclasses import dataclass, field
from loguru import logger
from open_webui.config import (
    GLOBUS_CLIENT_ID,
    GLOBUS_CLIENT_SECRET,
    GLOBUS_HIGH_ASSURANCE_POLICY,
    AUTHORIZED_IDP_DOMAINS,
    AUTHORIZED_GROUPS_PER_IDP
)

# Pydantic class to structure relevant user information from token introspection data
class UserPydantic(BaseModel):
    id: str
    name: str
    username: str
    domain: str
    idp_id: str
    idp_name: str
    auth_service: str


# Data structure returned by the access token validation function
class ATVResponse(BaseModel):
    is_valid: bool
    user: Optional[UserPydantic] = None
    user_group_uuids: List[str] = field(default_factory=lambda: [])
    idp_group_overlap_str: Optional[str] = None
    error_message: str = ""
    error_code: int = 0
    

# Redis-compatible token introspection with fallback to in-memory cache
def introspect_token(bearer_token: str):
    """
    Introspect a token with policy and group checks.
    Returns serializable data instead of Globus SDK objects.
    """

    # Create Globus SDK confidential client
    try:
        client = globus_sdk.ConfidentialAppAuthClient(GLOBUS_CLIENT_ID.value, GLOBUS_CLIENT_SECRET.value)
    except Exception as e:
        return None, [], f"Error: Could not create Globus confidential client. {e}"

    # Include the access token and the Globus policy
    introspect_body = {
        "token": bearer_token,
        "authentication_policies": GLOBUS_HIGH_ASSURANCE_POLICY.value,
        "include": "session_info,identity_set_detail"
    }

    # Introspect the token through the Globus Auth API (including policy evaluation)
    try: 
        introspection = client.post("/v2/oauth2/token/introspect", data=introspect_body, encoding="form")
    except Exception as e:
        return None, [], f"Error: Could not introspect token with Globus /v2/oauth2/token/introspect. {e}"
    
    # Error if the token is invalid
    if introspection["active"] is False:
        return None, [], "Error: Token is either not active or invalid"
    
    # Get dependent access token to view group membership
    
    #try:
    #    dependent_tokens = client.oauth2_get_dependent_tokens(bearer_token)
    #    access_token = dependent_tokens.by_resource_server["groups.api.globus.org"]["access_token"]
    #except Exception as e:
    #    return None, [], f"Error: Could not recover dependent access token for groups.api.globus.org. {e}"

    # Create a Globus Group Client using the access token sent by the user
    #try:
    #    authorizer = globus_sdk.AccessTokenAuthorizer(access_token)
    #    groups_client = globus_sdk.GroupsClient(authorizer=authorizer)
    #except Exception as e:
    #    return None, [], f"Error: Could not create GroupsClient. {e}"

    # Get the list of user's group memberships
    #try:
    #    user_groups_response = groups_client.get_my_groups()
    #    user_groups = [group["id"] for group in user_groups_response]
    #except Exception as e:
    #    return None, [], f"Error: Could not recover user group memberships. {e}"
    
    # !!!!!!! TO REMOVE !!!!!!!
    user_groups = [] # !!!!!!! TO REMOVE !!!!!!!
    # !!!!!!! TO REMOVE !!!!!!!
        
    # Return the introspection data along with the group (with empty error message)
    return introspection, user_groups, ""


# Check Globus Policies
def check_globus_policies(introspection):
    """
        Define whether an authenticated user respect the Globus policies.
        User should meet all Globus policies requirements.
    """

    # Return False if the user failed to meet one of the policies 
    for policies in introspection["policy_evaluations"].values():
        if policies.get("evaluation",False) == False:
            return False, f"Permission denied. Make sure to authenticate with an authorized identity provider: {AUTHORIZED_IDP_DOMAINS}."

    # Return True if the user met all of the policies requirements
    return True, ""
    

# Check Session Info
def check_session_info(introspection):
    """
        Look into the session_info field of the token introspection
        and collect the user information tied to the selected 
        authorized identity providers.
    """

    # Try to check if an authentication came from authorized provider
    try:

        # Define the list of IdP providers present in the session_info field
        # This array is used to log un-authorized attempts
        session_info_idp_ids = []

        # For each authentication in the session_info field ...
        for _, auth in introspection["session_info"]["authentications"].items():
            session_info_idp_ids.append(auth["idp"])

            # Find the user identity linked to the session's identity provider
            for identity in introspection["identity_set_detail"]:
                if auth["idp"] == identity["identity_provider"]:

                    # If the session's identity provider is authorized ...
                    if identity["username"].split("@")[1] in AUTHORIZED_IDP_DOMAINS.value:

                        # Create the User object from the Globus introspection
                        try:
                            user = UserPydantic(
                                id=identity["sub"],
                                name=identity["name"],
                                username=identity["username"],
                                domain=identity["username"].split("@")[1],
                                idp_id=identity["identity_provider"],
                                idp_name=identity["identity_provider_display_name"],
                                auth_service="Globus"
                            )
                        except Exception as e:
                            return False, None, f"Error: Could not create User object: {e}"

                        # Return successful check along with user details
                        return True, user, ""
            
    # Revoke access if something went wrong during the check
    except Exception as e:
        logger.error(f"Error: Could not inspect session info: {e}")
        return False, None, f"Error: Could not inspect session info: {e}"
    
    # If user not authorized, extract user details for error message
    try:
        user_str = []
        for identity in introspection["identity_set_detail"]:
            if identity["identity_provider"] in session_info_idp_ids:
                user_str.append(f"{identity['name']} ({identity['username']})")
        user_str = ", ".join(user_str)
    except Exception as e:
        logger.error(f"Error: Could not recover user identity: {e}")
        user_str = "could not recover user identity"
    
    # Revoke access if authentication did not come from authorized provider
    logger.info("will return now")
    logger.info(f"AUTHORIZED_IDP_DOMAINS {AUTHORIZED_IDP_DOMAINS.value}")
    logger.info(f"user_str {user_str}")
    return False, None, f"Error: Permission denied. Must authenticate with {AUTHORIZED_IDP_DOMAINS.value}. Currently authenticated as {user_str}."


# Check Session Info
def check_groups_per_idp(user: UserPydantic, user_groups: List[str]):
    """
        Make sure the user is part of an authorized Globus Group (if any)
        associated with a given identity provider.

        Returns: True/False if granted or not, error_message, group_overlap
    """
    
    # If there is a Globus Group check tied to the user's selected identity provider ...
    if user.domain in AUTHORIZED_GROUPS_PER_IDP.value:

        # Error if the user is a member of any authorized Globus Groups
        group_overlap = set(user_groups) & set(AUTHORIZED_GROUPS_PER_IDP.value[user.domain])
        if len(group_overlap) == 0:
            return False, f"Error: Permission denied. User ({user.name} - {user.username}) not part of the Globus Groups applied for {user.idp_name}.", None
        
        # Grant request if user is part of at least one authorized Globus Groups
        else:
            group_overlap = ", ".join(list(group_overlap))
            return True, "", group_overlap

    # Grant request if no group restriction was found
    return True, "", None


# Validate access token sent by user
def validate_access_token(bearer_token: str) -> ATVResponse:
    """This function returns an instance of the ATVResponse pydantic data structure."""

    logger.info("Starting access token validation")

    # Introspect the access token
    introspection, user_groups, error_message = introspect_token(bearer_token)
    if len(error_message) > 0:
        return ATVResponse(is_valid=False, error_message=f"Token introspection: {error_message}", error_code=401)

    logger.info(f"Token introspection result: {introspection}")

    # Make sure the token is not expired
    expires_in = introspection["exp"] - time.time()
    if expires_in <= 0:
        return ATVResponse(is_valid=False, error_message="Error: Access token expired.", error_code=401)

    logger.info(f"Token expires in: {expires_in} seconds")
    
    # Make sure the authentication was made by an authorized identity provider
    successful, user, error_message = check_session_info(introspection)
    if not successful:
        return ATVResponse(is_valid=False, error_message=error_message, error_code=403)

    logger.info(f"Session info check completed - successful: {successful}, user: {user}, error: {error_message}")

    # Make sure the authenticated user comes from an allowed domain
    # Those must be a high-assurance policies
    successful, error_message = check_globus_policies(introspection)
    if not successful:
        return ATVResponse(is_valid=False, error_message=error_message, error_code=403)

    logger.info(f"Globus policies check completed - successful: {successful}")
        
    # Make sure the user is part of a per-IdP authorized group (if any)
    successful, error_message, idp_group_overlap_str = check_groups_per_idp(user, user_groups)
    if not successful:
        return ATVResponse(is_valid=False, error_message=error_message, error_code=403)

    logger.info(f"Groups per IdP check completed - successful: {successful}, error: {error_message}, group overlap: {idp_group_overlap_str}")

    # Make sure the user's identity can be recorded
    if len(user.name) == 0 or len(user.username) == 0:
        return ATVResponse(is_valid=False, error_message="Error: Name and usernames could not be recovered.", error_code=400)

    logger.info(f"User validation - name: {user.name}, username: {user.username}")

    # Return valid token response
    return ATVResponse(
        is_valid=True,
        user=user,
        user_group_uuids=user_groups,
        idp_group_overlap_str=idp_group_overlap_str,
    )