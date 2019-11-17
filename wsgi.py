from dummy_flask import create_app

application = create_app()

if __name__ == "__main__":
    from run_server import run

    run(application)
