Help on class Client in module google.genai.client:

class CClliieenntt(builtins.object)
 |  Client(*, vertexai: Optional[bool] = None, api_key: Optional[str] = None, credentials: Optional[google.auth.credentials.Credentials] = None, project: Optional[str] = None, location: Optional[str] = None, debug_config: Optional[google.genai.client.DebugConfig] = None, http_options: Union[google.genai.types.HttpOptions, google.genai.types.HttpOptionsDict, NoneType] = None)
 |  
 |  Client for making synchronous requests.
 |  
 |  Use this client to make a request to the Gemini Developer API or Vertex AI
 |  API and then wait for the response.
 |  
 |  To initialize the client, provide the required arguments either directly
 |  or by using environment variables. Gemini API users and Vertex AI users in
 |  express mode can provide API key by providing input argument
 |  `api_key="your-api-key"` or by defining `GOOGLE_API_KEY="your-api-key"` as an
 |  environment variable
 |  
 |  Vertex AI API users can provide inputs argument as `vertexai=True,
 |  project="your-project-id", location="us-central1"` or by defining
 |  `GOOGLE_GENAI_USE_VERTEXAI=true`, `GOOGLE_CLOUD_PROJECT` and
 |  `GOOGLE_CLOUD_LOCATION` environment variables.
 |  
 |  Attributes:
 |    api_key: The `API key <https://ai.google.dev/gemini-api/docs/api-key>`_ to
 |      use for authentication. Applies to the Gemini Developer API only.
 |    vertexai: Indicates whether the client should use the Vertex AI API
 |      endpoints. Defaults to False (uses Gemini Developer API endpoints).
 |      Applies to the Vertex AI API only.
 |    credentials: The credentials to use for authentication when calling the
 |      Vertex AI APIs. Credentials can be obtained from environment variables and
 |      default credentials. For more information, see `Set up Application Default
 |      Credentials
 |      <https://cloud.google.com/docs/authentication/provide-credentials-adc>`_.
 |      Applies to the Vertex AI API only.
 |    project: The `Google Cloud project ID
 |      <https://cloud.google.com/vertex-ai/docs/start/cloud-environment>`_ to use
 |      for quota. Can be obtained from environment variables (for example,
 |      ``GOOGLE_CLOUD_PROJECT``). Applies to the Vertex AI API only.
 |      Find your `Google Cloud project ID <https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects>`_.
 |    location: The `location
 |      <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations>`_
 |      to send API requests to (for example, ``us-central1``). Can be obtained
 |      from environment variables. Applies to the Vertex AI API only.
 |    debug_config: Config settings that control network behavior of the client.
 |      This is typically used when running test code.
 |    http_options: Http options to use for the client. These options will be
 |      applied to all requests made by the client. Example usage: `client =
 |      genai.Client(http_options=types.HttpOptions(api_version='v1'))`.
 |  
 |  Usage for the Gemini Developer API:
 |  
 |  .. code-block:: python
 |  
 |    from google import genai
 |  
 |    client = genai.Client(api_key='my-api-key')
 |  
 |  Usage for the Vertex AI API:
 |  
 |  .. code-block:: python
 |  
 |    from google import genai
 |  
 |    client = genai.Client(
 |        vertexai=True, project='my-project-id', location='us-central1'
 |    )
 |  
 |  Methods defined here:
 |  
 |  ____ddeell____(self) -> None
 |  
 |  ____eenntteerr____(self) -> 'Client'
 |  
 |  ____eexxiitt____(self, exc_type: Optional[Exception], exc_value: Optional[Exception], traceback: Optional[traceback]) -> None
 |  
 |  ____iinniitt____(self, *, vertexai: Optional[bool] = None, api_key: Optional[str] = None, credentials: Optional[google.auth.credentials.Credentials] = None, project: Optional[str] = None, location: Optional[str] = None, debug_config: Optional[google.genai.client.DebugConfig] = None, http_options: Union[google.genai.types.HttpOptions, google.genai.types.HttpOptionsDict, NoneType] = None)
 |      Initializes the client.
 |      
 |      Args:
 |         vertexai (bool): Indicates whether the client should use the Vertex AI
 |           API endpoints. Defaults to False (uses Gemini Developer API endpoints).
 |           Applies to the Vertex AI API only.
 |         api_key (str): The `API key
 |           <https://ai.google.dev/gemini-api/docs/api-key>`_ to use for
 |           authentication. Applies to the Gemini Developer API only.
 |         credentials (google.auth.credentials.Credentials): The credentials to use
 |           for authentication when calling the Vertex AI APIs. Credentials can be
 |           obtained from environment variables and default credentials. For more
 |           information, see `Set up Application Default Credentials
 |           <https://cloud.google.com/docs/authentication/provide-credentials-adc>`_.
 |           Applies to the Vertex AI API only.
 |         project (str): The `Google Cloud project ID
 |           <https://cloud.google.com/vertex-ai/docs/start/cloud-environment>`_ to
 |           use for quota. Can be obtained from environment variables (for example,
 |           ``GOOGLE_CLOUD_PROJECT``). Applies to the Vertex AI API only.
 |         location (str): The `location
 |           <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations>`_
 |           to send API requests to (for example, ``us-central1``). Can be obtained
 |           from environment variables. Applies to the Vertex AI API only.
 |         debug_config (DebugConfig): Config settings that control network behavior
 |           of the client. This is typically used when running test code.
 |         http_options (Union[HttpOptions, HttpOptionsDict]): Http options to use
 |           for the client.
 |  
 |  cclloossee(self) -> None
 |      Closes the synchronous client explicitly.
 |      
 |      However, it doesn't close the async client, which can be closed using the
 |      Client.aio.aclose() method or using the async context manager.
 |      
 |      Usage:
 |      .. code-block:: python
 |      
 |        from google.genai import Client
 |      
 |        client = Client(
 |            vertexai=True, project='my-project-id', location='us-central1'
 |        )
 |        response_1 = client.models.generate_content(
 |            model='gemini-2.0-flash',
 |            contents='Hello World',
 |        )
 |        response_2 = client.models.generate_content(
 |            model='gemini-2.0-flash',
 |            contents='Hello World',
 |        )
 |        # Close the client to release resources.
 |        client.close()
 |  
 |  ----------------------------------------------------------------------
 |  Readonly properties defined here:
 |  
 |  aaiioo
 |  
 |  aauutthh__ttookkeennss
 |  
 |  bbaattcchheess
 |  
 |  ccaacchheess
 |  
 |  cchhaattss
 |  
 |  ffiillee__sseeaarrcchh__ssttoorreess
 |  
 |  ffiilleess
 |  
 |  iinntteerraaccttiioonnss
 |  
 |  mmooddeellss
 |  
 |  ooppeerraattiioonnss
 |  
 |  ttuunniinnggss
 |  
 |  vveerrtteexxaaii
 |      Returns whether the client is using the Vertex AI API.
 |  
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |  
 |  ____ddiicctt____
 |      dictionary for instance variables
 |  
 |  ____wweeaakkrreeff____
 |      list of weak references to the object
Help on class Client in module google.genai.client:

class CClliieenntt(builtins.object)
 |  Client(*, vertexai: Optional[bool] = None, api_key: Optional[str] = None, credentials: Optional[google.auth.credentials.Credentials] = None, project: Optional[str] = None, location: Optional[str] = None, debug_config: Optional[google.genai.client.DebugConfig] = None, http_options: Union[google.genai.types.HttpOptions, google.genai.types.HttpOptionsDict, NoneType] = None)
 |  
 |  Client for making synchronous requests.
 |  
 |  Use this client to make a request to the Gemini Developer API or Vertex AI
 |  API and then wait for the response.
 |  
 |  To initialize the client, provide the required arguments either directly
 |  or by using environment variables. Gemini API users and Vertex AI users in
 |  express mode can provide API key by providing input argument
 |  `api_key="your-api-key"` or by defining `GOOGLE_API_KEY="your-api-key"` as an
 |  environment variable
 |  
 |  Vertex AI API users can provide inputs argument as `vertexai=True,
 |  project="your-project-id", location="us-central1"` or by defining
 |  `GOOGLE_GENAI_USE_VERTEXAI=true`, `GOOGLE_CLOUD_PROJECT` and
 |  `GOOGLE_CLOUD_LOCATION` environment variables.
 |  
 |  Attributes:
 |    api_key: The `API key <https://ai.google.dev/gemini-api/docs/api-key>`_ to
 |      use for authentication. Applies to the Gemini Developer API only.
 |    vertexai: Indicates whether the client should use the Vertex AI API
 |      endpoints. Defaults to False (uses Gemini Developer API endpoints).
 |      Applies to the Vertex AI API only.
 |    credentials: The credentials to use for authentication when calling the
 |      Vertex AI APIs. Credentials can be obtained from environment variables and
 |      default credentials. For more information, see `Set up Application Default
 |      Credentials
 |      <https://cloud.google.com/docs/authentication/provide-credentials-adc>`_.
 |      Applies to the Vertex AI API only.
 |    project: The `Google Cloud project ID
 |      <https://cloud.google.com/vertex-ai/docs/start/cloud-environment>`_ to use
 |      for quota. Can be obtained from environment variables (for example,
 |      ``GOOGLE_CLOUD_PROJECT``). Applies to the Vertex AI API only.
 |      Find your `Google Cloud project ID <https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects>`_.
 |    location: The `location
 |      <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations>`_
 |      to send API requests to (for example, ``us-central1``). Can be obtained
 |      from environment variables. Applies to the Vertex AI API only.
 |    debug_config: Config settings that control network behavior of the client.
 |      This is typically used when running test code.
 |    http_options: Http options to use for the client. These options will be
 |      applied to all requests made by the client. Example usage: `client =
 |      genai.Client(http_options=types.HttpOptions(api_version='v1'))`.
 |  
 |  Usage for the Gemini Developer API:
 |  
 |  .. code-block:: python
 |  
 |    from google import genai
 |  
 |    client = genai.Client(api_key='my-api-key')
 |  
 |  Usage for the Vertex AI API:
 |  
 |  .. code-block:: python
 |  
 |    from google import genai
 |  
 |    client = genai.Client(
 |        vertexai=True, project='my-project-id', location='us-central1'
 |    )
 |  
 |  Methods defined here:
 |  
 |  ____ddeell____(self) -> None
 |  
 |  ____eenntteerr____(self) -> 'Client'
 |  
 |  ____eexxiitt____(self, exc_type: Optional[Exception], exc_value: Optional[Exception], traceback: Optional[traceback]) -> None
 |  
 |  ____iinniitt____(self, *, vertexai: Optional[bool] = None, api_key: Optional[str] = None, credentials: Optional[google.auth.credentials.Credentials] = None, project: Optional[str] = None, location: Optional[str] = None, debug_config: Optional[google.genai.client.DebugConfig] = None, http_options: Union[google.genai.types.HttpOptions, google.genai.types.HttpOptionsDict, NoneType] = None)
 |      Initializes the client.
 |      
 |      Args:
 |         vertexai (bool): Indicates whether the client should use the Vertex AI
 |           API endpoints. Defaults to False (uses Gemini Developer API endpoints).
 |           Applies to the Vertex AI API only.
 |         api_key (str): The `API key
 |           <https://ai.google.dev/gemini-api/docs/api-key>`_ to use for
 |           authentication. Applies to the Gemini Developer API only.
 |         credentials (google.auth.credentials.Credentials): The credentials to use
 |           for authentication when calling the Vertex AI APIs. Credentials can be
 |           obtained from environment variables and default credentials. For more
 |           information, see `Set up Application Default Credentials
 |           <https://cloud.google.com/docs/authentication/provide-credentials-adc>`_.
 |           Applies to the Vertex AI API only.
 |         project (str): The `Google Cloud project ID
 |           <https://cloud.google.com/vertex-ai/docs/start/cloud-environment>`_ to
 |           use for quota. Can be obtained from environment variables (for example,
 |           ``GOOGLE_CLOUD_PROJECT``). Applies to the Vertex AI API only.
 |         location (str): The `location
 |           <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations>`_
 |           to send API requests to (for example, ``us-central1``). Can be obtained
 |           from environment variables. Applies to the Vertex AI API only.
 |         debug_config (DebugConfig): Config settings that control network behavior
 |           of the client. This is typically used when running test code.
 |         http_options (Union[HttpOptions, HttpOptionsDict]): Http options to use
 |           for the client.
 |  
 |  cclloossee(self) -> None
 |      Closes the synchronous client explicitly.
 |      
 |      However, it doesn't close the async client, which can be closed using the
 |      Client.aio.aclose() method or using the async context manager.
 |      
 |      Usage:
 |      .. code-block:: python
 |      
 |        from google.genai import Client
 |      
 |        client = Client(
 |            vertexai=True, project='my-project-id', location='us-central1'
 |        )
 |        response_1 = client.models.generate_content(
 |            model='gemini-2.0-flash',
 |            contents='Hello World',
 |        )
 |        response_2 = client.models.generate_content(
 |            model='gemini-2.0-flash',
 |            contents='Hello World',
 |        )
 |        # Close the client to release resources.
 |        client.close()
 |  
 |  ----------------------------------------------------------------------
 |  Readonly properties defined here:
 |  
 |  aaiioo
 |  
 |  aauutthh__ttookkeennss
 |  
 |  bbaattcchheess
 |  
 |  ccaacchheess
 |  
 |  cchhaattss
 |  
 |  ffiillee__sseeaarrcchh__ssttoorreess
 |  
 |  ffiilleess
 |  
 |  iinntteerraaccttiioonnss
 |  
 |  mmooddeellss
 |  
 |  ooppeerraattiioonnss
 |  
 |  ttuunniinnggss
 |  
 |  vveerrtteexxaaii
 |      Returns whether the client is using the Vertex AI API.
 |  
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |  
 |  ____ddiicctt____
 |      dictionary for instance variables
 |  
 |  ____wweeaakkrreeff____
 |      list of weak references to the object
