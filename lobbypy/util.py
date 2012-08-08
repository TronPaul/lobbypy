def _assign(obj, name, parent):
    obj.__name__ = name
    obj.__parent__ = parent
    return obj

def openid(context, request, openid):
    print openid['identity_url']
