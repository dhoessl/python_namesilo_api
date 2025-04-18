#!/usr/bin/env python3

from requests.models import Response
from requests import get
from . import errors


class RecordValueError(errors.RecordError):
    def __init__(self, *args) -> None:
        if args:
            value = args[0]
            self.message = f"Value {value} is not set!"
        else:
            self.message = errors.RecordError.generic_message

    def __str__(self) -> str:
        return self.message


class RecordExistsError(errors.RecordError):
    def __init__(self, *args) -> None:
        if args:
            self.id = args[0]
            self.host = args[1]
            self.type = args[2]
            self.new_host = args[3]
            self.new_type = args[4]
            self.message = f"Record with {self.new_host} and " \
                + f"{self.new_type} already exists. ID: {self.id} - " \
                + f"host: {self.host} - type: {self.type}"
        else:
            self.message = errors.RecordError.generic_message

    def __str__(self) -> str:
        return self.message


class RecordIDNotFoundError(errors.RecordError):
    def __init__(self, *args) -> None:
        if args:
            self.message = f"Record ID {args[0]} was not found!"
        else:
            self.message = errors.RecordError.generic_message

    def __str__(self) -> str:
        return self.message


class RecordHostTypeNotFoundError(errors.RecordError):
    def __init__(self, *args) -> None:
        if args:
            self.message = f"Record using host {args[0]} and type "\
                + f"{args[1]} was not found!"
        else:
            self.message = errors.RecordError.generic_message

    def __str__(self) -> str:
        return self.message


class NamesiloAPIReturnError(errors.NamesiloAPIError):
    def __init__(self, *args) -> None:
        if args:
            self.function = args[0] if len(args) >= 1 else None
            self.domain = args[1] if len(args) >= 2 else None
            self.host = args[2] if len(args) >= 3 else None

    def __str__(self) -> str:
        if self.domain:
            return f"Api Call on {self.function} with domain" \
                + f" {self.domain} and host {self.host}"
        else:
            return errors.NamesiloAPIError.generic_message \
                + ": Api Call was not successfull"


class Domain:
    def __init__(self, key: str, domain: str) -> None:
        """ Class to manage all hosts of a specific domain.
            domain and api key are required to fetch all data.
        """
        self.domain = domain
        self.api_uri = "https://www.namesilo.com/api/"
        self.api_opts = f"?version=1&type=json&key={key}"
        self.records = []

    def get_records(self) -> None:
        """ Request all data for a domain from api.
            for every host an Record object is created and put into
            self.records list.
        """
        api_response = get(
            f"{self.api_uri}dnsListRecords{self.api_opts}&domain={self.domain}"
        )
        if api_response.json()["reply"]["detail"] != "success":
            raise NamesiloAPIReturnError("List Domains", self.domain)
        # Clear current saved records
        self.records = []
        # Add new records to domain
        for record in api_response.json()["reply"]["resource_record"]:
            new_record = Record(self.api_opts, self.domain)
            new_record.set_values_from_api(record)
            self.records.append(new_record)

    def create_record(
            self,
            host: str, record_type: str, value: str,
            ttl: int = None, distance: int = None
    ) -> None:
        """ Creates a new record. If the record already exists (host + type)
            raise an Error
        """
        # Check if record already exists
        for record in self.records:
            if record.host == host and record_type == record.type:
                raise RecordExistsError(
                    record.id, record.host, record.type, host, record_type
                )
        # record does not exist, so create a new one
        record = Record(self.api_opts, self.domain)
        record.set_values(
            host, record_type, value,
            ttl=ttl, distance=distance
        )
        if record.add_record():
            self.records.append(record)

    def delete_record_by_id(self, id: str) -> None:
        """ Searches Record based on id and deletes it """
        for record in self.records:
            if record.id == id:
                record.delete_record()
                return
        raise RecordIDNotFoundError(id)

    def delete_record_by_host_type(self, host: str, record_type: str) -> None:
        """ Searches Record based on host and record type and deletes it """
        for record in self.records:
            if record.host == host and record.type == record_type:
                record.delete_record()
                return
        raise RecordHostTypeNotFoundError(host, record_type)

    def update_record_by_id(
        self, id: str, value: str = None,
        ttl: int = None, distance: int = None
    ) -> None:
        # Search record to update
        for record in self.records:
            if record.id == id:
                update_record = record
        # var to check if update is needed
        update_needed = False
        # update values
        if value and update_record.value != value:
            update_record.value = value
            update_needed = True
        if ttl and update_record.ttl != ttl:
            update_record.ttl = ttl
            update_needed = True
        if distance and update_record.distance != distance:
            update_record.distance = distance
            update_needed = True
        # Update record if required
        if update_needed:
            update_record.update_record()

    def update_record_by_host_type(
        self, host: str, record_type: str,
        value: str = None, ttl: int = None, distance: int = None
    ) -> None:
        # Search for record by host and record type
        for record in self.records:
            if record.host == host and record.type == record_type:
                self.update_record_by_id(
                    record.id, value=value,
                    ttl=ttl, distance=distance
                )


class Record:
    allowed_types = ["A", "AAAA", "CNAME", "MX", "TXT", "SRV", "CAA"]

    def __init__(
            self,
            api_opts: str,
            domain: str
    ) -> None:
        """ Class to manage a ressource record """
        self.api_uri = "https://www.namesilo.com/api/"
        self.api_opts = api_opts
        self.domain = domain
        self.id = None
        self.host = None
        self.type = None
        self.value = None
        self.ttl = None
        self.distance = None
        self.active = None

    def delete_record(self) -> bool:
        if not self.id:
            raise RecordValueError("id")
        record_opts = f"&domain={self.domain}&rrid={self.id}"
        response = self.send_request("dnsDeleteRecord", record_opts)
        if response.json()["reply"]["detail"] != "success":
            raise NamesiloAPIReturnError(
                "delete record", self.domain, self.host
            )
        self.active = False
        return True

    def update_record(self) -> bool:
        self.check_values()
        if not self.id:
            raise RecordValueError("id")
        if self.get_current_type() != self.type:
            self.delete_record()
            self.add_record()
            return True
        update_opts = f"&domain={self.domain}&rrid={self.id}" \
            + f"&rrhost={self.host}&rrvalue={self.value}&rrttl={self.ttl}"
        if self.type == "MX":
            update_opts += f"&rrdistance{self.distance}"
        response = self.send_request("dnsUpdateRecord", update_opts)
        if response.json()["reply"]["detail"] != "success":
            raise NamesiloAPIReturnError(
                "update record", self.domain, self.host
            )
        self.id = response.json()["reply"]["record_id"]
        return True

    def add_record(self) -> bool:
        """ Add Record to domain """
        self.check_values()
        record_opts = f"&domain={self.domain}&rrtype={self.type}" \
            + f"&rrhost={self.host}&rrvalue={self.value}&rrttl={self.ttl}"
        if self.type == "MX":
            if not self.distance:
                raise RecordValueError("distance")
            record_opts += f"&rrdistance={self.distance}"
        response = self.send_request("dnsAddRecord", record_opts)
        if response.json()["reply"]["detail"] != "success":
            raise NamesiloAPIReturnError(
                "add record",
                self.domain,
                self.host
            )
        self.id = response.json()["reply"]["record_id"]
        self.active = True
        return True

    def get_current_type(self) -> str:
        response = get(
            f"{self.api_uri}dnsListRecords{self.api_opts}&domain={self.domain}"
        )
        for host in response.json()["reply"]["resource_record"]:
            if host["record_id"] == self.id:
                return host["type"]

    def send_request(self, call: str, request_opts: str) -> Response:
        return get(f"{self.api_uri}{call}{self.api_opts}{request_opts}")

    def set_values(
        self,
        host: str, record_type: str, value: str,
        ttl: int = None, distance: int = None, id: str = None
    ) -> None:
        if record_type not in Record.allowed_types:
            raise RecordValueError(
                f"{record_type} is not one of "
                f"[{', '.join(Record.allowed_types)}]"
            )
        self.id = id if id else None
        self.host = host
        self.type = record_type
        self.value = value
        self.ttl = ttl if ttl else 7207
        self.distance = distance if distance else 10

    def set_values_from_api(self, record: dict) -> None:
        """ Set record information from data send by the api. """
        self.set_values(
            record["host"].replace(f".{self.domain}", ""),
            record["type"], record["value"], ttl=record["ttl"],
            distance=record["distance"] if "distance" in record else None,
            id=record["record_id"]
        )
        self.active = True

    def check_values(self) -> None:
        if not self.host:
            raise RecordValueError("host")
        if not self.type:
            raise RecordValueError("type")
        if not self.value:
            raise RecordValueError("value")
        if not self.ttl:
            raise RecordValueError("ttl")
