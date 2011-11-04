
hook =None


def setHook(_hook):
    hook = _hook

def log(text):
    if hook:
        hook(text)
    else:
        print(text)

