"""Defines the ChatIoT Conversation backend."""
from __future__ import annotations

from .utils.logs import _logger

_logger.debug(f"Start conversation.py")

from typing import Literal

from homeassistant.components.conversation import ConversationInput, ConversationResult, AbstractConversationAgent, ConversationEntity
from homeassistant.components import assist_pipeline, conversation as ha_conversation
from homeassistant.components.conversation.const import DOMAIN as CONVERSATION_DOMAIN
from homeassistant.components.homeassistant.exposed_entities import async_should_expose
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, intent, entity_registry as er, area_registry as ar, device_registry as dr
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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

from .chatiot.config_chatiot import CONFIG

_logger.debug(f"conversation.py: module import completed")

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> bool:
    """Set up ChatIoT Conversation from a config entry."""

    def create_agent(provider):
        agent_cls = None

        if provider in PROVIDERS:
            agent_cls = GenericOpenAIAPIAgent
        else:
            _logger.error(f"Unsupported provider: {provider}")
            raise ValueError(f"Unsupported provider: {provider}")
        
        return agent_cls(hass, entry)

    provider = entry.data.get(CONF_PROVIDER, DEFAULT_PROVIDER)
    agent = await hass.async_add_executor_job(create_agent, provider)

    await agent._async_load_model(entry)

    async_add_entities([agent])

    return True

class LocalLLMAgent(ConversationEntity, AbstractConversationAgent):
    """Base Local LLM conversation agent."""
    hass: HomeAssistant
    entry_id: str
    history: dict[str, list[dict]]

    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self._attr_name = entry.title
        self._attr_unique_id = entry.entry_id
        self._attr_supported_features = (
            ha_conversation.ConversationEntityFeature.CONTROL
        )

        self.hass = hass
        self.entry_id = entry.entry_id
        self.history = {}

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        assist_pipeline.async_migrate_engine(
            self.hass, "conversation", self.entry.entry_id, self.entity_id
        )
        ha_conversation.async_set_agent(self.hass, self.entry, self)
    
    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from Home Assistant."""
        ha_conversation.async_unset_agent(self.hass, self.entry)
        await super().async_will_remove_from_hass()

    @property
    def entry(self) -> ConfigEntry:
        try:
            return self.hass.data[DOMAIN][self.entry_id]
        except KeyError as ex:
            raise Exception("Attempted to use self.entry during startup.") from ex
        
    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    def _load_model(self, entry: ConfigEntry) -> None:
        """Load the model on the backend. Implemented by sub-classes"""
        raise NotImplementedError()

    async def _async_load_model(self, entry: ConfigEntry) -> str:
        """Default implementation is to call _load_model() which probably does blocking stuff"""
        return await self.hass.async_add_executor_job(
            self._load_model, entry
        )
    
    def _generate(self, conversation: dict) -> str:
        """Call the backend to generate a response from the conversation. Implemented by sub-classes"""
        raise NotImplementedError()

    async def _async_generate(self, conversation: dict) -> str:
        """Default implementation is to call _generate() which probably does blocking stuff"""
        return await self.hass.async_add_executor_job(
            self._generate, conversation
        )

    def _warn_context_size(self):
        raise NotImplementedError()

    async def async_process(
        self, user_input: ConversationInput
    ) -> ConversationResult:
        _logger.debug(f"Processing conversation: {user_input.text}")
        """Process a sentence."""

        # if user_input.conversation_id in self.history:
        #     conversation_id = user_input.conversation_id
        #     conversation = self.history[conversation_id]
        conversation_id = user_input.conversation_id
        conversation = []

        conversation.append({"role": "user", "message": user_input.text})
            
        # generate a response
        try:
            _logger.debug(conversation)
            response = await self._async_generate(conversation)
            _logger.debug(response)

        except Exception as err:
            _logger.error("There was a problem talking to the backend")
            
            intent_response = intent.IntentResponse(language=user_input.language)
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.FAILED_TO_HANDLE,
                f"Sorry, there was a problem talking to the backend: {repr(err)}",
            )
            return ConversationResult(
                response=intent_response, conversation_id=conversation_id
            )
        
        conversation.append({"role": "assistant", "message": response})

        self.history[conversation_id] = conversation
        
        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(response.strip())

        return ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )      

    def _async_get_exposed_entities(self) -> tuple[dict[str, str], list[str]]:
        """Gather exposed entity states"""
        entity_states = {}
        domains = set()
        entity_registry = er.async_get(self.hass)
        device_registry = dr.async_get(self.hass)
        area_registry = ar.async_get(self.hass)

        for state in self.hass.states.async_all():
            if not async_should_expose(self.hass, CONVERSATION_DOMAIN, state.entity_id):
                continue

            entity = entity_registry.async_get(state.entity_id)
            device = None
            if entity and entity.device_id:
                device = device_registry.async_get(entity.device_id)

            attributes = dict(state.attributes)
            attributes["state"] = state.state

            if entity:
                if entity.aliases:
                    attributes["aliases"] = entity.aliases
                    
                if entity.unit_of_measurement:
                    attributes["state"] = attributes["state"] + " " + entity.unit_of_measurement

            # area could be on device or entity. prefer device area
            area_id = None
            if device and device.area_id:
                area_id = device.area_id
            if entity and entity.area_id:
                area_id = entity.area_id
            
            if area_id:
                area = area_registry.async_get_area(entity.area_id)
                if area:
                    attributes["area_id"] = area.id
                    attributes["area_name"] = area.name
            
            entity_states[state.entity_id] = attributes
            domains.add(state.domain)

        return entity_states, list(domains)


class GenericOpenAIAPIAgent(LocalLLMAgent):
    """Generic OpenAI API conversation agent."""
    provider: str
    api_key: str
    base_url: str
    temperature: float
    max_tokens: int

    async def _async_load_model(self, entry: ConfigEntry) -> None:
        self.provider = self.entry.data.get(CONF_PROVIDER, DEFAULT_PROVIDER)
        self.api_key = self.entry.data.get(CONF_API_KEY, DEFAULT_API_KEY)
        self.base_url = self.entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL)
        self.temperature = self.entry.data.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
        self.max_tokens = self.entry.data.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS)
        CONFIG.configs["provider"] = self.provider
        CONFIG.configs["api_key"] = self.api_key
        CONFIG.configs["base_url"] = self.base_url
        CONFIG.configs["temperature"] = self.temperature
        CONFIG.configs["max_tokens"] = self.max_tokens
    
    async def _async_generate(self, conversation: dict) -> str:
        from .chatiot.jarvis import test_1
        if conversation[0]["message"] == "hello":
            return "Hello, how can I help you today?"
        elif conversation[0]["message"] == "你好":
            return "你好，我是你的智能家居助手Jarvis，有什么可以帮到您的吗？"
        else:
            try:
                return await test_1(conversation[0]["message"])
            except:
                return "Sorry, The server is not available now. Please wait the server to be online."

        

    

