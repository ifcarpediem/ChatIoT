"""Config flow for ChatIoT Conversation integration."""
from __future__ import annotations

from .utils.logs import _logger

_logger.debug(f"Start config_flow.py")

from abc import ABC, abstractmethod
from typing import Any

import voluptuous as vol

from homeassistant import config_entries

from homeassistant.data_entry_flow import (
    FlowHandler,
    FlowManager,
    FlowResult,
)

from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    DOMAIN,
    CONF_PROVIDER,
    CONF_API_KEY,
    CONF_BASE_URL,
    CONF_TEMPERATURE,
    CONF_MAX_TOKENS,
    PROVIDERS,
    DEFAULT_PROVIDER,
    DEFAULT_API_KEY,
    DEFAULT_BASE_URL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS
)

_logger.debug(f"config_flow.py: module import completed")

def STEP_CONFIG_PROVIDER_SCHEMA(provider=None, api_key=None, base_url=None, temperature=None, max_tokens=None):
    return vol.Schema(
        {
            vol.Required(
                CONF_PROVIDER,
                default=provider if provider else DEFAULT_PROVIDER
            ): SelectSelector(
                SelectSelectorConfig(
                    options=PROVIDERS,
                    multiple=False,
                    mode=SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Required(CONF_API_KEY, default=api_key if api_key else DEFAULT_API_KEY): str,
            vol.Required(CONF_BASE_URL, default=base_url if base_url else DEFAULT_BASE_URL): str,
            vol.Required(CONF_TEMPERATURE, default=temperature if temperature else DEFAULT_TEMPERATURE): NumberSelector(
                NumberSelectorConfig(
                    min=0.0,
                    max=1.0,
                    step=0.1)),
            vol.Required(CONF_MAX_TOKENS, default=max_tokens if max_tokens else DEFAULT_MAX_TOKENS): NumberSelector(
                NumberSelectorConfig(
                    min=1,
                    max=2048,
                    step=1))
        }
    )

class BaseChatiotConversationConfigFlow(FlowHandler, ABC):
    """Represent the base config flow for Z-Wave JS."""

    @property
    @abstractmethod
    def flow_manager(self) -> FlowManager:
        """Return the flow manager of the flow."""

    @abstractmethod
    async def async_step_config_provider(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Config provider."""

    @abstractmethod
    async def async_step_finish(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """ Finish configuration """   

class ConfigFlow(BaseChatiotConversationConfigFlow, config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ChatIoT Conversation."""

    VERSION = 1
    provider_config: dict[str, Any]

    @property
    def flow_manager(self) -> config_entries.ConfigEntriesFlowManager:
        """Return the correct flow manager."""
        return self.hass.config_entries.flow
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        _logger.debug("Starting user step")
        """Handle the initial step."""
        self.provider_config = {}

        return await self.async_step_config_provider()

    async def _async_validate_generic_openai(self, user_input) -> tuple:
        _logger.debug("Validating connection to OpenAI API server")
        """
        Validates a connection to an OpenAI compatible API server and that the model exists on the remote server

        :param user_input: the input dictionary used to build the connection
        :return: a tuple of (error message name, exception detail); both can be None
        """
        try:
            _logger.debug("Attempting to connect to OpenAI API server")

            from openai import OpenAI
            import httpx

            _api_key = user_input.get(CONF_API_KEY)
            _base_url = user_input.get(CONF_BASE_URL)

            client = OpenAI(
                api_key=_api_key,
                base_url=_base_url,
                http_client=httpx.Client(
                    base_url=_base_url,
                    follow_redirects=True,
                ),
            )

            completion = client.chat.completions.create(
                model=user_input.get(CONF_PROVIDER),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"}
                ]
            )

            _logger.debug(f"Completion was: {completion}")

            return None, None

        except Exception as ex:
            _logger.error(f"Connection error was: {repr(ex)}")
            return "failed_to_connect", repr(ex)

    async def async_step_config_provider(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        _logger.debug("Starting config provider step")
        """Handle the provider configuration."""
        errors = {}
        description_placeholders = {}

        _logger.debug("Before schema creation")

        schema = STEP_CONFIG_PROVIDER_SCHEMA()

        _logger.debug("After schema creation")

        if user_input:
            _logger.debug(f"User input was: {user_input}")
            try:
                self.provider_config.update(user_input)
                error_message, exception = await self._async_validate_generic_openai(user_input)
                # error_message, exception = None, None

                _logger.debug(f"Error message was: {error_message}")
                _logger.debug(f"Exception was: {exception}")

                if error_message:
                    errors["base"] = error_message
                    if exception:
                        description_placeholders["exception"] = str(exception)
                    schema = STEP_CONFIG_PROVIDER_SCHEMA(
                        provider=user_input.get(CONF_PROVIDER),
                        api_key=user_input.get(CONF_API_KEY),
                        base_url=user_input.get(CONF_BASE_URL),
                        temperature=user_input.get(CONF_TEMPERATURE),
                        max_tokens=user_input.get(CONF_MAX_TOKENS)
                    )
                else:
                    return await self.async_step_finish()
            except Exception:
                _logger.error("Unexpected error")
                errors["base"] = "unknown_error"

        return self.async_show_form(
            step_id="config_provider", data_schema=schema, errors=errors,description_placeholders=description_placeholders,last_step=False
        )

    async def async_step_finish(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        _logger.debug("Starting finish step")
        """Finish configuration."""
        return self.async_create_entry(
            title="ChatIoT Conversation",
            description="A LLM-based Multi-Agent Chatbot for Home Assistant",
            data = self.provider_config
        )

   




      
