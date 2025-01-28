funclist = [
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Used to send a message using teams",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to send"
                    },
                    "person": {
                        "type": "string",
                        "description": "The person to send the message to"
                    }
                },
                "required": ["message", "person"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Used to open an application",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "The name of the application to open"
                    }
                },
                "required": ["app_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_email",
            "description": "Used to read an email",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_info",
            "description": "Used to get information about current date/time, and any system/connection information",
            "parameters": {
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "description": "The question to ask"
                    }
                },
                "required": ["input"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "learn_function",
            "description": "Used to learn a new function",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "The command to run"}}
            }
        }
    }
]