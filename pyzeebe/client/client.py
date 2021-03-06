from typing import Dict, List

import grpc

from pyzeebe.credentials.base_credentials import BaseCredentials
from pyzeebe.grpc_internals.zeebe_adapter import ZeebeAdapter


class ZeebeClient(object):
    """A zeebe client that can connect to a zeebe instance and perform actions."""

    def __init__(self, hostname: str = None, port: int = None, credentials: BaseCredentials = None,
                 channel: grpc.Channel = None, secure_connection: bool = False, max_connection_retries: int = 10):
        """
        Args:
            hostname (str): Zeebe instance hostname
            port (int): Port of the zeebe
            max_connection_retries (int): Amount of connection retries before client gives up on connecting to zeebe. To setup with infinite retries use -1
        """

        self.zeebe_adapter = ZeebeAdapter(hostname=hostname, port=port, credentials=credentials, channel=channel,
                                          secure_connection=secure_connection,
                                          max_connection_retries=max_connection_retries)

    def run_workflow(self, bpmn_process_id: str, variables: Dict = None, version: int = -1) -> int:
        """
        Run workflow

        Args:
            bpmn_process_id (str): The unique process id of the workflow.
            variables (dict): A dictionary containing all the starting variables the workflow needs. Must be JSONable.
            version (int): The version of the workflow. Default: -1 (latest)

        Returns:
            int: workflow_instance_key, the unique id of the running workflow generated by Zeebe.

        Raises:
            WorkflowNotFound: No workflow with bpmn_process_id exists
            InvalidJSON: variables is not JSONable
            WorkflowHasNoStartEvent: The specified workflow does not have a start event
            ZeebeBackPressure: If Zeebe is currently in back pressure (too many requests)
            ZeebeGatewayUnavailable: If the Zeebe gateway is unavailable
            ZeebeInternalError: If Zeebe experiences an internal error

        """
        return self.zeebe_adapter.create_workflow_instance(bpmn_process_id=bpmn_process_id, variables=variables or {},
                                                           version=version)

    def run_workflow_with_result(self, bpmn_process_id: str, variables: Dict = None, version: int = -1,
                                 timeout: int = 0, variables_to_fetch: List[str] = None) -> Dict:
        """
        Run workflow and wait for the result.

        Args:
            bpmn_process_id (str): The unique process id of the workflow.
            variables (dict): A dictionary containing all the starting variables the workflow needs. Must be JSONable.
            version (int): The version of the workflow. Default: -1 (latest)
            timeout (int): How long to wait until a timeout occurs. Default: 0 (Zeebe default timeout)
            variables_to_fetch (List[str]): Which variables to get from the finished workflow

        Returns:
            dict: A dictionary of the end state of the workflow instance

        Raises:
            WorkflowNotFound: No workflow with bpmn_process_id exists
            InvalidJSON: variables is not JSONable
            WorkflowHasNoStartEvent: The specified workflow does not have a start event
            ZeebeBackPressure: If Zeebe is currently in back pressure (too many requests)
            ZeebeGatewayUnavailable: If the Zeebe gateway is unavailable
            ZeebeInternalError: If Zeebe experiences an internal error

        """
        return self.zeebe_adapter.create_workflow_instance_with_result(bpmn_process_id=bpmn_process_id,
                                                                       variables=variables or {}, version=version,
                                                                       timeout=timeout,
                                                                       variables_to_fetch=variables_to_fetch or [])

    def cancel_workflow_instance(self, workflow_instance_key: int) -> int:
        """
        Cancel a running workflow instance

        Args:
            workflow_instance_key (int): The key of the running workflow to cancel

        Returns:
            int: The workflow_instance_key

        Raises:
            WorkflowInstanceNotFound: If no workflow instance with workflow_instance_key exists
            ZeebeBackPressure: If Zeebe is currently in back pressure (too many requests)
            ZeebeGatewayUnavailable: If the Zeebe gateway is unavailable
            ZeebeInternalError: If Zeebe experiences an internal error

        """
        self.zeebe_adapter.cancel_workflow_instance(workflow_instance_key=workflow_instance_key)
        return workflow_instance_key

    def deploy_workflow(self, *workflow_file_path: str) -> None:
        """
        Deploy one or more workflows

        Args:
            workflow_file_path (str): The file path to a workflow definition file (bpmn/yaml)

        Raises:
            WorkflowInvalid: If one of the workflow file definitions is invalid
            ZeebeBackPressure: If Zeebe is currently in back pressure (too many requests)
            ZeebeGatewayUnavailable: If the Zeebe gateway is unavailable
            ZeebeInternalError: If Zeebe experiences an internal error

        """
        self.zeebe_adapter.deploy_workflow(*workflow_file_path)

    def publish_message(self, name: str, correlation_key: str, variables: Dict = None,
                        time_to_live_in_milliseconds: int = 60000, message_id: str = None) -> None:
        """
        Publish a message

        Args:
            name (str): The message name
            correlation_key (str): The correlation key. For more info: https://docs.zeebe.io/glossary.html?highlight=correlation#correlation-key
            variables (dict): The variables the message should contain.
            time_to_live_in_milliseconds (int): How long this message should stay active. Default: 60000 ms (60 seconds)
            message_id (str): A unique message id. Useful for avoiding duplication. If a message with this id is still
                                active, a MessageAlreadyExists will be raised.

        Raises:
            MessageAlreadyExist: If a message with message_id already exists
            ZeebeBackPressure: If Zeebe is currently in back pressure (too many requests)
            ZeebeGatewayUnavailable: If the Zeebe gateway is unavailable
            ZeebeInternalError: If Zeebe experiences an internal error

        """
        self.zeebe_adapter.publish_message(name=name, correlation_key=correlation_key,
                                           time_to_live_in_milliseconds=time_to_live_in_milliseconds,
                                           variables=variables or {}, message_id=message_id)
