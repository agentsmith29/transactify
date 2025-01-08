from requests_unixsocket import Session
import logging
from typing import Optional, Dict, Any
import inspect
from functools import wraps
from typing import Optional, Any




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

    def get_assignment(func):
        """
        Decorator to capture the outer variable that has been assigned to.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Inspect the stack to get the name of the outer variable being assigned
            frame = inspect.currentframe().f_back
            try:
                # Extract the source code of the calling frame
                calling_code = inspect.getframeinfo(frame).code_context
                if not calling_code:
                    raise ValueError("Unable to extract source code context.")

                # Get the line where the function is called
                assignment_line = calling_code[0].strip()

                # Parse the outer variable name from the assignment statement
                if "=" in assignment_line:
                    outer_var = assignment_line.split("=")[0].strip()
                    kwargs["assigned_to"] = outer_var
                else:
                    raise ValueError("Function call is not part of an assignment statement.")
            except Exception as e:
                raise RuntimeError(f"Failed to determine outer variable: {e}")

            # Call the original function with the modified kwargs
            return func(*args, **kwargs)

        return wrapper

    @get_assignment
    def assign_from_config(self, key: str, default: Optional[str] = None, required: Optional[bool] = None, assigned_to: str = None) -> Any:
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

        _value = self._assign(key, _value, assigned_to)
        
        if required:
            self.print(f"[{assigned_to.replace('self', self.field_name)}*]: {key}: {_value}")
        else:
            self.print(f"[{assigned_to.replace('self', self.field_name)}]: {key}: {_value}")

        return _value

    @get_assignment
    def assign_direct(self, value: Any, assigned_to: str = None) -> Any:
        assigned_to = assigned_to.replace("self.", "")
        return self._assign(key=assigned_to, value=value, assigned_to=assigned_to)

    def _assign(self, key: str, value: Any, assigned_to: str) -> Any:
        self._keywords[f"{self.field_name}.{key}"] = value
        if assigned_to and "self" in assigned_to:
            assigned_to = assigned_to.replace("self.", "")
        self._members[f"{self.field_name}.{assigned_to}"] = value
        setattr(self, assigned_to, value)
        reg_field = getattr(self, assigned_to)
        self.logger.debug(f"Registered: {assigned_to} = {reg_field}")
        return value

    def _replace_inconfig(self, value: Optional[str], depth=1) -> str:
        if value is None:
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
            setattr(self, member_attr, _value)
            self.print(f"{_value}")
            reg_field = getattr(self, member_attr)
            self.logger.debug(f"Replaced: {member_attr} = {reg_field}")
        self.finalize_initialization()

            
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
