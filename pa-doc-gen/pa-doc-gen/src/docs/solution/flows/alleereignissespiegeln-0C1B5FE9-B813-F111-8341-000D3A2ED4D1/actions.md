# Flow-Struktur – Aktionen

## Aktionshierarchie

- **Elemente_abrufen_-_alle_ereignisse** *(OpenApiConnection)* `[SharePoint]`
- **For_each** *(Foreach)*
  - Run After: Succeeded
  - **Bedingung_-_nicht_gelöscht** *(If)*
    - **Element_erstellen_-_M365-Sprechstunden** *(OpenApiConnection)* `[SharePoint]`
    - **Bedingung_-_nicht_gelöscht – Ja** *(Branch_True)*
      - **Element_erstellen_-_M365-Sprechstunden** *(OpenApiConnection)* `[SharePoint]`

---

## Aktionen im Detail


### Elemente_abrufen_-_alle_ereignisse

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

### For_each

| Eigenschaft | Wert |
|---|---|
| Typ | `Foreach` |
| Run After | Succeeded |

#### Bedingung_-_nicht_gelöscht

| Eigenschaft | Wert |
|---|---|
| Typ | `If` |

##### Element_erstellen_-_M365-Sprechstunden

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

##### Bedingung_-_nicht_gelöscht – Ja

| Eigenschaft | Wert |
|---|---|
| Typ | `Branch_True` |

###### Element_erstellen_-_M365-Sprechstunden

| Eigenschaft | Wert |
|---|---|
| Typ | `OpenApiConnection` |
| Connector | SharePoint |

