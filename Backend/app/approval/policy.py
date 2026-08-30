SENSITIVE_ACTIONS ={
    "send_email":{
        "requires_approval":True,
        "risk":"HIGH"
    },
    "publish_report":{
        "requires_approval":True,
        "risk":"HIGH"
    },
    "delete_document":{
        "requires_approval":True,
        "risk":"CRITICAL"
    },
    "calculator":{
        "requires_approval":False,
        "risk":"LOW"
    },
    "web_search":{
        "requires_approval":False,
        "risk":"LOW"
    }
}

def requires_approval(action:str)->bool:
    config=SENSITIVE_ACTIONS.get(
        action
    )
    if not config:
        return True
    return config["requires_approval"]