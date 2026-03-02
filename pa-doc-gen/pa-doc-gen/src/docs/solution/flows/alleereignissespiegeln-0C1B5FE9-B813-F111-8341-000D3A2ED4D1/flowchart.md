# Flussdiagramm

## Flow-Visualisierung

```mermaid
flowchart TD
    TRIGGER(["⚡ manual\n(Request)"])
    Elemente_abrufen_alle_ereignisse_7984["Elemente_abrufen_-_alle_ereignisse\n[SharePoint]"]
    TRIGGER --> Elemente_abrufen_alle_ereignisse_7984
    For_each_5968[["For_each"]]
    Elemente_abrufen_alle_ereignisse_7984 --> For_each_5968
    Bedingung_nicht_gel_scht_6864{{"Bedingung_-_nicht_gelöscht"}}
    For_each_5968 --> Bedingung_nicht_gel_scht_6864
    Bedingung_nicht_gel_scht_Ja_5072(["Bedingung_-_nicht_gelöscht – Ja"])
    Bedingung_nicht_gel_scht_6864 -->|Ja| Bedingung_nicht_gel_scht_Ja_5072
    Element_erstellen_M365_Sprechstunden_4080["Element_erstellen_-_M365-Sprechstunden\n[SharePoint]"]
    Bedingung_nicht_gel_scht_Ja_5072 --> Element_erstellen_M365_Sprechstunden_4080
    Element_erstellen_M365_Sprechstunden_6416["Element_erstellen_-_M365-Sprechstunden\n[SharePoint]"]
    Bedingung_nicht_gel_scht_6864 --> Element_erstellen_M365_Sprechstunden_6416
    FLOW_END(["Ende"])
    Element_erstellen_M365_Sprechstunden_4080 --> FLOW_END
    Element_erstellen_M365_Sprechstunden_6416 --> FLOW_END

    class TRIGGER trigger
    class Elemente_abrufen_alle_ereignisse_7984 connector
    class For_each_5968 loop
    class Bedingung_nicht_gel_scht_6864 condition
    class Bedingung_nicht_gel_scht_Ja_5072 branch_true
    class Element_erstellen_M365_Sprechstunden_4080 connector
    class Element_erstellen_M365_Sprechstunden_6416 connector
    class FLOW_END terminate

    %% Styles
    classDef trigger fill:#5B8DEF,stroke:#3A6FD8,color:#fff,stroke-width:2px
    classDef action fill:#1E2233,stroke:#5B8DEF,color:#E0E0E0,stroke-width:1px
    classDef connector fill:#1A3A5C,stroke:#5B8DEF,color:#E0E0E0,stroke-width:1px
    classDef condition fill:#E0A526,stroke:#C48F20,color:#fff,stroke-width:2px
    classDef loop fill:#9C27B0,stroke:#7B1FA2,color:#fff,stroke-width:2px
    classDef scope fill:#2E3B4E,stroke:#5B8DEF,color:#E0E0E0,stroke-width:1px,stroke-dasharray: 5 5
    classDef branch_true fill:#4CAF50,stroke:#388E3C,color:#fff,stroke-width:1px
    classDef branch_false fill:#EF5B5B,stroke:#D32F2F,color:#fff,stroke-width:1px
    classDef variable fill:#00897B,stroke:#00695C,color:#fff,stroke-width:1px
    classDef data fill:#546E7A,stroke:#37474F,color:#fff,stroke-width:1px
    classDef http fill:#FF7043,stroke:#E64A19,color:#fff,stroke-width:1px
    classDef terminate fill:#EF5B5B,stroke:#D32F2F,color:#fff,stroke-width:2px
```


### Legende

| Farbe | Bedeutung |
|---|---|
| 🔵 Blau | Trigger / Standard-Aktion |
| 🟡 Gelb | Bedingung (If/Switch) |
| 🟣 Lila | Schleife (Foreach/Until) |
| 🟢 Gruen | Ja-Zweig / Case |
| 🔴 Rot | Nein-Zweig / Default / Ende |
| 🟤 Orange | HTTP-Aktionen |
| 🔷 Tuerkis | Variablen-Aktionen |
| ⬜ Grau | Daten-Operationen (Compose, ParseJson) |

