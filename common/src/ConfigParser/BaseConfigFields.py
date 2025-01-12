from requests_unixsocket import Session
import logging
from typing import Optional, Dict, Any
import inspect
from functools import wraps
from typing import Optional, Any
import re
from .capture_assigned_var import capture_assigned_var
import os

class BaseConfigField:
    def __init__(self, data: Dict[str, Any], field_name: str, logger: logging.Logger):
        self.logger = logger
        self.field_name = field_name

        self.data = data
        self._env = self.data['env']                            # Stores the environment variables
        self._content = self.data['content']                    # Stores the unaltered content
        self._field_content = self._content.get(field_name, {}) # Stores the unaltered content
        self._keywords = self.data['keywords']                  # Stores the keywords     
        self._members = {}
        self._members_apply_functions = {}

        self._debug_print = False
        self._initialized = False  # Tracks if the instance has been fully initialized

    def print(self, *args, **kwargs):
        if self._debug_print:
            print(*args, **kwargs)

    def _flatten_dict(self, data: dict) -> dict:
        # Flatten the data
        _data_flat = {}
        for key, value in data.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    _data_flat[f"{key}.{k}"] = v
            else:
                _data_flat[key] = value
        return _data_flat

    @capture_assigned_var()
    def assign_from_config(self, key: str, default: Optional[str] = None, required: Optional[bool] = None,
                           lambda_apply_func: callable = None,
                           assigned_to: str = None) -> Any:
        """
        Assign a configuration value, replacing placeholders as needed.
        """
        if required is None:
            required = default is None or default == ""
        

        try:
            _value = self._field_content.get(key, default)
            if _value is None:
                if required:
                    raise ValueError(f"Required key {key} not found in the config.")
                else:
                    _value = default
        except Exception as e:
            _value = default
            self.logger.error(f"Error accessing key {key}: {e}")
            raise ValueError(f"Error accessing key {key}: {e}")

        _value = self._assign(key, _value, assigned_to, lambda_apply_func)
        
        if required:
            self.print(f"[{assigned_to.replace('self', self.field_name)}*]: {key}: {_value}")
        else:
            self.print(f"[{assigned_to.replace('self', self.field_name)}]: {key}: {_value}")
        
        return _value

    @capture_assigned_var()
    def assign_direct(self, value: Any, assigned_to: str = None) -> Any:
        assigned_to = assigned_to.replace("self.", "")
        return self._assign(key=assigned_to, value=value, assigned_to=assigned_to)

    def _assign(self, key: str, value: Any, assigned_to: str, lambda_apply_func: callable=None) -> Any:
        self._keywords[f"{self.field_name}.{key}"] = value
        if assigned_to and "self" in assigned_to:
            assigned_to = assigned_to.replace("self.", "")
        self._members[f"{self.field_name}.{assigned_to}"] = value
        self._members_apply_functions[f"{self.field_name}.{assigned_to}"] = lambda_apply_func
        setattr(self, assigned_to, value)
        reg_field = getattr(self, assigned_to)
        self.logger.debug(f"Registered: {assigned_to} = {reg_field}")
        return value

    def _replace_inconfig(self, value: Optional[str], depth=1) -> str:
        if value is None or isinstance(value, bool) or isinstance(value, int) or isinstance(value, float):
            return value  # If value is None, return it unchanged

        for key, data_val in self._keywords.items():
            if f"${{{key}}}" in value:
                value = value.replace(f"${{{key}}}", data_val)
                self.print(f"{value} -> ", end="")
            # also check, if the member without fieldname. is in the value7
            key_without_fieldname = key.replace(f"{self.field_name}.", '') 
            if f"${{{key_without_fieldname}}}" in value:
                value = value.replace(f"${{{key.split('.')[1]}}}", data_val)
                self.print(f"{value} -> ", end="")

        for env_key, env_value in self._env.items():
            if f"${{ENV.{env_key}}}" in value:
                value = value.replace(f"${{ENV.{env_key}}}", env_value)
                self.print(f"{value} -> ", end="")

        if depth >= 3:
            self.print(f"[{depth}] DEPTH REACHED -> ", end="")

        if "${" in value and "}" in value and depth < 3:
            self.print(f'[R/{depth}] -> ', end='')
            value = self._replace_inconfig(value, depth + 1)
        else:
            self.print(f'[O/{depth}] -> ', end="")

        return value

    def replace_keywords(self):
        self.print("\n\n\n*** Replacing keywords ***\n")
        for key, value in self._members.items():
            member_attr = key.split(".")[1]
            self.print(f"Replacing keywords in {key} -> ", end="")
            _value = self._replace_inconfig(value)
            # Apply the lambda function if one is defined
            lambda_apply_func = self._members_apply_functions.get(key)
            if lambda_apply_func:
                _value = lambda_apply_func(_value)
            setattr(self, member_attr, _value)
            self.print(f"{_value}")
            reg_field = getattr(self, member_attr)
            self.logger.debug(f"Replaced: {member_attr} = {reg_field}")
            # set it as global variable
            os.environ[member_attr] = str(reg_field)
        self.finalize_initialization()

    # =================================================================================================================
    # Functios for wrapping some values
    # =================================================================================================================
    def wrap_url(self, url: str, protocol: str) -> str:
        # Check and prepend protocol if not given
        if not re.match(r'^[a-zA-Z]+://', url):
            url = f"{protocol}://{url}"

        # Validate the final URL format
        #pattern = re.compile(r'^[a-zA-Z]+://(?:[a-zA-Z0-9.-]+|\d{1,3}(?:\.\d{1,3}){3}):\d{1,5}/[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+)*$')
        pattern = re.compile(r'^[a-zA-Z]+://(?:[a-zA-Z0-9.-]+|\d{1,3}(?:\.\d{1,3}){3}):\d{1,5}(?:/[a-zA-Z0-9._-]+)*$')
        # Thank you ChatGTP for this weird regex pattern
        if not pattern.match(url):
            raise ValueError(f"Invalid URL format: {url}")

        return url
            
    def __setattr__(self, name, value):
        if hasattr(self, "_initialized") and self._initialized:
            raise AttributeError(f"Cannot modify attribute '{name}' after initialization.")
        super().__setattr__(name, value)

    def __str__(self) -> str:
        str_repr = f"[{self.field_name}]\n"
        for key, value in self._members.items():
            attrval = getattr(self, key.split(".")[1])
            str_repr += f"  {key}: {attrval}\n"

        return str_repr

    def finalize_initialization(self):
        """
        Marks the class as fully initialized, preventing further changes to attributes.
        """
        self.logger.info(f"Finalizing initialization of {self.field_name}")
        self._initialized = True
