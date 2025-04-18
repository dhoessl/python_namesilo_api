# Install
```
pip install -U git+https://github.com/dhoessl/python_namesilo_api
```

# Functions
### Domain.get_records()
args:
 * None
### Domain.create_record()
args:
* host (required, positional)
* record_type (required, positional)
* value (required, positional)
* ttl=None (keyword)
* distance=None (keyword)
### Domain.delete_record_by_id()
args:
* id (required, positional)
### Domain.delete_record_by_host_type()
args:
* host (required, positional)
* record_type (required, positional)
### Domain.update_record_by_id()
args:
* id (required, positional)
* value (keyword)
* ttl (keyword)
* distance (keyword)
### Domain.update_record_by_host_type()
args:
* host (required, positional)
* record_type (required, positional)
* value (keyword)
* ttl (keyword)
* distance (keyword)


# Example
## Fetch Data
```
In [1]: from namesilo_api import Domain
In [2]: domain = Domain(api_key, "dhoessl.de")
In [3]: domain.get_records()
In [4]: for record in domain.records:
   ...:     print(f"===\n{record.id}\n{record.host}\n{record.type}\n{record.value}\n{record.ttl}\n{record.distance}\n{record.active}\n")
===
ID
ip
A
207.180.243.190
3600
10
True
[...]
```
## Add record
```
domain.create_record("ip", "A", "207.180.243.190")
```
## Delete record
```
domain.delete_record_by_id(ID)
domain.delete_record_by_host_type("ip", "A")
```
## Update record
```
domain.update_record_by_id(ID, "127.0.0.1", ttl=7207)
domain.update_record_by_host_type("ip", "A", "127.0.0.1", ttl=7207)
```
