import logging
import os
from datetime import datetime, timedelta

import arvados
from arvados.errors import ApiError

from arvados_cwl_tester.entities import Project, Container, Process, Collection
from arvados_cwl_tester.exceptions import (
    ProjectNotFoundError,
    ProcessNotFoundError,
    CollectionNotFoundError,
)

from arvados_cwl_tester.helpers import get_git_username


class ArvadosClient:
    def __init__(self):
        self.api = arvados.api("v1")

    def get_project(self, uuid: str) -> Project:
        """
        Get project by uuid
        """
        try:
            response = self.api.groups().get(uuid=uuid).execute()
            return Project.from_dict(**response)
        except ApiError as e:
            if e.resp.status == 404:
                raise ProjectNotFoundError(f"No project with uuid {uuid}")
            raise

    def get_collection(self, uuid: str) -> Collection:
        """
        Get collection by uuid
        """
        try:
            response = self.api.collections().get(uuid=uuid).execute()
            return Collection.from_dict(**response)
        except ApiError as e:
            if e.resp.status == 404:
                raise CollectionNotFoundError(f"No collection with uuid {uuid}")
            raise

    def create_project(self, parent_uuid: str, test_name: str) -> Project:
        """
        Create test project in target project. Trash it after one week.
        :param parent_uuid: Target project uuid
        :return: dictionary with project data
        """

        git_username = get_git_username()
        subproject_name = f"{test_name} {datetime.now():%Y-%m-%d %H:%M:%S}"

        if git_username:
            subproject_name = f"{subproject_name} {git_username}"

        response = (
            self.api.groups()
            .create(
                body={
                    "group_class": "project",
                    "owner_uuid": parent_uuid,
                    "name": subproject_name,
                    "trash_at": (datetime.now() + timedelta(days=7)).strftime(
                        "%Y-%m-%d"
                    ),
                }
            )
            .execute()
        )
        return Project.from_dict(**response)

    def list_container_requests_in_project(self, parent_uuid: str):
        return arvados.util.keyset_list_all(
            self.api.container_requests().list,
            filters=[["owner_uuid", "=", parent_uuid]],
        )

    def get_container_request_by_parent_uuid(self, parent_uuid: str) -> Process:
        """
        Return first container request from parent project. Raise exception if empty
        :param parent_uuid:
        :return:
        """
        requests = list(self.list_container_requests_in_project(parent_uuid))
        if not requests:
            raise ProcessNotFoundError(
                f"No processes are found in {parent_uuid} project"
            )
        if len(requests) > 1:
            logging.warning(f"Multiple processes found in {parent_uuid}")
        response = requests[0]
        container = self.get_container(response["container_uuid"])
        return Process.from_dict(**response, container=container)

    def get_container(self, uuid: str) -> Container:
        try:
            response = self.api.containers().get(uuid=uuid).execute()
            return Container.from_dict(**response)
        except ApiError as e:
            if e.resp.status == 404:
                raise ProcessNotFoundError(f"No container with uuid {uuid}")
            raise

    def get_container_request(self, uuid: str) -> Process:
        try:
            response = self.api.container_requests().get(uuid=uuid).execute()
            if response["container_uuid"]:
                container = self.get_container(response["container_uuid"])
            else:
                container = None
            return Process.from_dict(**response, container=container)
        except ApiError as e:
            if e.resp.status == 404:
                raise ProcessNotFoundError(f"No container with uuid {uuid}")
            raise
