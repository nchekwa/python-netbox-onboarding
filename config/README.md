# Config file example

```yaml
tenants:
  - name: Administrator
  - name: CompanyA
  - name: CompanyB
  - name: CompanyC

sites:
  - name: Paris DC1
    tenant: Administrator
  - name: Warsaw DC1
    tenant: Administrator

device-roles: 
  - name: spine
    vm_role: false
    color: 0099ff       # blue
  - name: leaf
    vm_role: 0
    color: 00cc00       # green

manufacturers:
  - name: 'Arista'
  - name: 'Cisco'
    description: "Cisco Networks"

...
[snipp]
```
