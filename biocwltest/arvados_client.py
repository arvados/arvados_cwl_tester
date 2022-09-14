import logging
from datetime import datetime, timedelta

import arvados
from arvados.errors import ApiError

from biocwltest.exceptions import ProjectNotFoundError, ProcessNotFoundError


class ArvadosClient:
    def __init__(self):
        self.api = arvados.api('v1')

    def get_project(self, uuid: str):
        """
        Get dictionary with project data
        """
        try:
            return self.api.groups().get(uuid=uuid).execute()
        except ApiError as e:
            if e.resp.status == 404:
                raise ProjectNotFoundError(f"No project with uuid {uuid}")
            raise

    def create_project(self, parent_uuid: str):
        """
        Create test project in target project. Trash it after one week.
        :param parent_uuid: Target project uuid
        :return: dictionary with project data
        """
        return self.api.groups().create(body={
            "group_class": "project",
            "owner_uuid": parent_uuid,
            "name": f'Testing workflow {datetime.now():%Y-%m-%d %H:%M:%S%z}',
            "trash_at": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        }).execute()

    def list_container_requests_in_project(self, parent_uuid: str):
        return arvados.util.keyset_list_all(
            self.api.container_requests().list,
            filters=[["owner_uuid", "=", parent_uuid]]
        )

    def get_container_request_by_parent_uuid(self, parent_uuid: str):
        """
        Return first container request from parent project. Raise exception if empty
        :param parent_uuid:
        :return:
        """
        requests = list(self.list_container_requests_in_project(parent_uuid))
        if not requests:
            raise ProcessNotFoundError(f"No processes are found in {parent_uuid} project")
        if len(requests) > 1:
            logging.warning(f"Multiple processes found in {parent_uuid}")
        return requests[0]

    def get_container(self, uuid: str):
        try:
            return self.api.containers().get(uuid=uuid).execute()
        except ApiError as e:
            if e.resp.status == 404:
                raise ProcessNotFoundError(f"No container with uuid {uuid}")
            raise
