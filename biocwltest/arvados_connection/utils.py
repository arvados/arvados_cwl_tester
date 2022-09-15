from biocwltest.arvados_connection.client import ArvadosClient


def create_new_project(target):
    # Create project in target
    client = ArvadosClient()
    project_uuid = client.create_project(target)['uuid']
    print(f"Project was created succesfully: {project_uuid}")
    return project_uuid
