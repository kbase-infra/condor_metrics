from uvicorn import run
from factory import create_app

if __name__ == "__main__":
    app_instance = create_app()
    run(app_instance, host="0.0.0.0", port=5001)
