import os


def check_env_vars():
    required = {"SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES"}
    missing = []

    for var in required:
        if var not in os.environ:
            missing.append(var)
    if missing:
        msg = f"Required missing environment variables {', '.join(missing)}"
        raise OSError(msg)


check_env_vars()
