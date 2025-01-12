import inspect
from functools import wraps

def capture_assigned_var(arg_name='assigned_to'):
    """
    Decorator to capture the outer variable that has been assigned to.
    The argument `arg_name` specifies the key to add the outer variable name in kwargs.
    """
    def decorator(func):
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
                    kwargs[arg_name] = outer_var  # Use the specified key for the variable name
                else:
                    raise ValueError("Function call is not part of an assignment statement.")
            except Exception as e:
                raise RuntimeError(f"Failed to determine outer variable: {e}")

            # Call the original function with the modified kwargs
            return func(*args, **kwargs)

        return wrapper

    return decorator
