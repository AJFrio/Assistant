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
            "name": "check_email",
            "description": "Used to check most recent emails",
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
                "properties": {
                    "command": {
                        "type": "string", 
                        "description": "The command to run"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Used to send an email",
            "parameters": {
                "type": "object",
                "properties": {
                    "people": {
                        "type": "string", 
                        "description": "The people to send the email to"
                    },
                    "cc": {
                        "type": "string",
                        "description": "The people to CC in the email"
                    },
                    "subject": {
                        "type": "string",
                        "description": "The subject of the email"
                    },
                    "message": {
                        "type": "string",
                        "description": "The message of the email"
                    }
                },
                "required": ["people", "subject", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_jira",
            "description": "Used to check for any recent Jira tickets, updates, etc.",
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
            "name": "update_cursor",
            "description": "Used to interact with Cursor",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt to use"
                    }
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_website",
            "description": "Used to check a website for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The url to check"
                    },
                    "context": {
                        "type": "string",
                        "description": "A summary of the question the user asked"
                    }
                },
                "required": ["url", "context"]
            }
        }
    }
]