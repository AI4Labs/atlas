

def deploy(project_name, entrypoint, params):
    import os
    import os.path as path
    import json

    from foundations_contrib.job_deployer import deploy_job
    from foundations_contrib.global_state import (
        current_foundations_context,
        redis_connection,
        config_manager,
    )
    from foundations_internal.pipeline_context_wrapper import PipelineContextWrapper

    if project_name is None:
        project_name = path.basename(os.getcwd())

    current_foundations_context().set_project_name(project_name)
    config_manager["run_script_environment"] = {
        "script_to_run": entrypoint,
        "enable_stages": False,
    }

    current_foundations_context().pipeline_context().provenance.user_name = (
        _get_user_name_from_token()
    )
    pipeline_context_wrapper = PipelineContextWrapper(
        current_foundations_context().pipeline_context()
    )

    if params is not None:
        with open("foundations_job_parameters.json", "w+") as params_file:
            json.dump(params, params_file)

    return deploy_job(pipeline_context_wrapper, None, {})


def _get_user_name_from_token() -> str:
    import requests
    from foundations_contrib.global_state import config_manager
    from foundations_authentication.user_token import user_token

    token = user_token()
    scheduler_url = config_manager.config().get("scheduler_url")
    headers = {"Authorization": f"Bearer {token}"}
    decoded_token = requests.get(
        f"{scheduler_url}/api/v2beta/auth/verify", headers=headers
    )

    try:
        user_name = decoded_token.json()["preferred_username"]
    except:
        user_name = "CE User"

    return user_name
