import json
import logging
import os
import socket
from collections import defaultdict

import htcondor
import socks
from pydantic import BaseModel, Field, computed_field

if os.environ.get("SOCKS_PROXY"):
    # For local development
    socks.setdefaultproxy(
        socks.SOCKS5, os.environ.get("SOCKS_PROXY"), os.environ.get("SOCKS_PROXY_PORT")
    )
    socket.socket = socks.socksocket

good_attrs = [
    "Machine",
    "SlotTypeID",
    "LoadAvg",
    "TotalCPUs",
    "CpuFamily",
    "Memory",
    "TotalVirtualMemory",
    "TotalSlots",
    "TotalSlotDisk",
    "Name",
    "SlotType",
    "CLIENTGROUP",
    "DetectedCpus",
    "DetectedMemory",
    "DetectedNetworkSpeed",
    "DetectedNetworkType",
    "DetectedNetworkMTU",
    "DetectedNetworkAutoNegotiate",
    "CondorVersion",
    "Cpus",
    "State",
    "EnteredCurrentState",
    "NODE_IS_HEALTHY",
]


class Slot(BaseModel):
    cpus: int = Field(alias="TotalCPUs")
    memory: int = Field(alias="TotalMemory")
    disk: int = Field(alias="TotalSlotDisk")


# Pydantic model for Machine
class Machine(BaseModel):
    slots: list = Field(default_factory=list)
    partitionable: bool = True  # or dynamic
    client_group: str = "default"
    total_cpus: int = 0
    child_cpus: list = []
    child_memory: list = []
    child_disk: list = []

    @computed_field
    def used_slots(self) -> int:
        if self.partitionable:
            return len(self.child_cpus)
        else:
            return -1
        # TODO Case for hpc clientgroup/ static slots

    @computed_field
    def reserved_cpus(self) -> int:
        if self.partitionable:
            return sum(self.child_cpus)
        # todo figure this out actually for hpc clientgroup
        return -1

    @computed_field
    def is_busy(self) -> int:
        if self.partitionable:
            return int(len(self.child_cpus) > 0)

        # TODO
        return -1

    def custom_serialize(self):
        # Convert the model to a dictionary
        data = self.model_dump()
        # Custom serialization for the 'slots' field
        data["slots"] = [self.serialize_slot(slot) for slot in data["slots"]]
        return json.dumps(data, indent=2)

    @staticmethod
    def serialize_slot(slot):
        slot_dict = dict(slot)

        # Filter the slot attributes
        filtered_slot = {
            attr: slot_dict.get(attr) for attr in good_attrs if attr in slot_dict
        }
        return filtered_slot


def get_condor_metrics():
    # Create a Collector object to interact with the HTCondor system
    COLLECTOR_HOST = os.environ.get("COLLECTOR_HOST")
    if not COLLECTOR_HOST:
        raise ValueError("COLLECTOR_HOST environment variable not set")

    collector = htcondor.Collector(pool=COLLECTOR_HOST)

    # Query the collector for the status of all machines in the pool
    machine_ads = collector.query(htcondor.AdTypes.Startd)

    # Initialize a dictionary to store machine stats
    machine_stats = defaultdict(Machine)

    # Process each machine advertisement
    for machine in machine_ads:
        machine_name = machine["Machine"]
        partitionable = machine["SlotType"] == "Partitionable"

        machine_stats[machine_name].slots.append(machine)

        if machine["SlotType"] == "Partitionable" or machine["SlotType"] == "Static":
            # skip dynamic slots which only appear when a job is running
            machine_stats[machine_name].total_cpus = machine["TotalCPUs"]
            machine_stats[machine_name].partitionable = partitionable
            machine_stats[machine_name].client_group = machine["CLIENTGROUP"]

        if machine["SlotType"] == "Partitionable":
            machine_stats[machine_name].child_cpus = machine["ChildCpus"]
            machine_stats[machine_name].child_memory = machine["ChildMemory"]
            machine_stats[machine_name].child_disk = machine["ChildDisk"]

    return machine_stats


def emit_is_busy(condor_ads):
    messages = []
    for machine_name, machine in sorted(condor_ads.items()):
        message = f'is_busy{{node="{machine_name}",clientgroup="{machine.client_group}"}} {machine.is_busy}'
        logging.info(message)
        messages.append(message)
    return messages


def emit_in_use_slots(condor_ads):
    messages = []
    for machine_name, machine in sorted(condor_ads.items()):
        message = f'in_use_slots{{node="{machine_name}",clientgroup="{machine.client_group}"}} {machine.used_slots}'
        logging.info(message)
        messages.append(message)
    return messages


def emit_node_in_use_cpus(condor_ads):
    messages = []
    for machine_name, machine in sorted(condor_ads.items()):
        message = f'in_use_cpus{{node="{machine_name}",clientgroup="{machine.client_group}"}} {machine.reserved_cpus}'
        logging.info(message)
        messages.append(message)
    return messages
