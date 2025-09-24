import aiohttp
from open_webui.config import GATEWAY_API_WHOAMI_URL
from open_webui.env import AIOHTTP_CLIENT_SESSION_SSL

async def validate_user_access_token(user_access_token):
    """
    Check if the user is authorized to use the Inference Gateway API.
    Returns True, whoami_data, None if the user is authorized.
    Returns False, None, error_message otherwise.
    """
    
    # Prepare URL and Headers to contact the Inference Gateway API
    url = GATEWAY_API_WHOAMI_URL.value
    headers = {"Authorization": f"Bearer {user_access_token}", "Content-Type": "application/json"}

    # Make a request to the Inference Gateway API to see if user is authorized
    try:
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url, headers=headers, ssl=AIOHTTP_CLIENT_SESSION_SSL) as whoami_response:
                whoami_data = await whoami_response.json()

                # If the request succeeded (meaning the user is authorized), return the whoami data
                if whoami_response.status == 200:
                    return True, whoami_data, None

                # If the request failed (likely due to unauthorized access) ...
                else:
                    
                    # Try to extract just the error message from the 'detail' field
                    try:
                        if isinstance(whoami_data, dict) and 'detail' in whoami_data:
                            error_message = whoami_data['detail']
                        else:
                            error_message = str(whoami_data)
                    except Exception:
                        error_message = str(whoami_data)

                    # Return the error message
                    return False, None, error_message

    # Deny access if something went wrong during the whoami call parsing            
    except Exception as e:
        error_message = f"Call to {url} failed: {e}"
        return False, None, error_message