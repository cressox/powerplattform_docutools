# Flow-Struktur – Aktionen

## Aktionshierarchie

- **Variable_initialisieren_-_Titel** *(InitializeVariable)*
- **Bedingung_-_ist_abgesagt** *(If)*
  - Run After: Succeeded
  - **Variable_festlegen_-Titel** *(SetVariable)*
    - Expression: `triggerBody()?['Title']`
  - **Bedingung_-_ist_abgesagt – Ja** *(Branch_True)*
    - **Variable_festlegen_-Titel** *(SetVariable)*
      - Expression: `triggerBody()?['Title']`
- **Element_aktualisieren_-_Ereignis** *(OpenApiConnection)* `[SharePoint]`
  - Run After: Succeeded

---

## Aktionen im Detail


### Variable_initialisieren_-_Titel

| Eigenschaft | Wert |
|---|---|
| Typ | `InitializeVariable` |

### Bedingung_-_ist_abgesagt

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |
| Run After | Succeeded |

#### Variable_festlegen_-Titel

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |

**Expression:**
```
triggerBody()?['Title']
```


#### Bedingung_-_ist_abgesagt – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

##### Variable_festlegen_-Titel

| Eigenschaft | Wert |
|---|---|
| Typ | `SetVariable` |

**Expression:**
```
triggerBody()?['Title']
```


### Element_aktualisieren_-_Ereignis

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |
| Run After | Succeeded |

