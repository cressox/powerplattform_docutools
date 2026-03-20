# Flussdiagramm

## Flow-Visualisierung

```mermaid
flowchart TD
    TRIGGER(["⚡ Recurrence\n(Recurrence)"])
    VZeitStempelStatusAbgeschlossen_3632["VZeitStempelStatusAbgeschlossen"]
    TRIGGER --> VZeitStempelStatusAbgeschlossen_3632
    VZeitStempelAngebotErstellt_3008["VZeitStempelAngebotErstellt"]
    VZeitStempelStatusAbgeschlossen_3632 --> VZeitStempelAngebotErstellt_3008
    VEndDatum_4608["VEndDatum"]
    VZeitStempelAngebotErstellt_3008 --> VEndDatum_4608
    VTempCheckIfNull_9520["VTempCheckIfNull"]
    VEndDatum_4608 --> VTempCheckIfNull_9520
    Elemente_abrufen_alle_Presales_Projekte_128["Elemente_abrufen_alle_Presales_Projekte\n[SharePoint]"]
    VTempCheckIfNull_9520 --> Elemente_abrufen_alle_Presales_Projekte_128
    Check_Status_Abgeschlossen_5424[["Check_Status_Abgeschlossen"]]
    Elemente_abrufen_alle_Presales_Projekte_128 --> Check_Status_Abgeschlossen_5424
    Setze_VDatumStatusAbgeschlossen_7680["Setze_VDatumStatusAbgeschlossen"]
    Check_Status_Abgeschlossen_5424 --> Setze_VDatumStatusAbgeschlossen_7680
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__9040{{"Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null"}}
    Setze_VDatumStatusAbgeschlossen_7680 --> Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__9040
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__9376(["Bedingung_E-Mail_Flow_Aktiv_und_ZeitStempel_nicht_null – Ja"])
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__9040 -->|Ja| Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__9376
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_48{{"Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt"}}
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__9376 --> Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_48
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3184(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_48 -->|Ja| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3184
    Setze_VDatumAngebotErstellt_4080["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3184 --> Setze_VDatumAngebotErstellt_4080
    Variable_festlegen_3632["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_4080 --> Variable_festlegen_3632
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4304{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_3632 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4304
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4528(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4304 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4528
    E_Mail_senden_V2_2_5200["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4528 --> E_Mail_senden_V2_2_5200
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4976(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4304 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4976
    Auftrag_gewonnen_5648{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4976 --> Auftrag_gewonnen_5648
    Auftrag_gewonnen_Ja_4928(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_5648 -->|Ja| Auftrag_gewonnen_Ja_4928
    Auftragsnummer_bekannt_5600{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_4928 --> Auftragsnummer_bekannt_5600
    Auftragsnummer_bekannt_Nein_5376(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_5600 -->|Nein| Auftragsnummer_bekannt_Nein_5376
    E_Mail_senden_V2_3_6048["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_5376 --> E_Mail_senden_V2_3_6048
    Auftragsnummer_bekannt_5872{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_5648 --> Auftragsnummer_bekannt_5872
    Auftragsnummer_bekannt_Nein_5424(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_5872 -->|Nein| Auftragsnummer_bekannt_Nein_5424
    E_Mail_senden_V2_3_5152["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_5424 --> E_Mail_senden_V2_3_5152
    E_Mail_senden_V2_2_4752["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4304 --> E_Mail_senden_V2_2_4752
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_5824(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_48 -->|Nein| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_5824
    Angebot_noch_offen_6496{{"Angebot_noch_offen"}}
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_5824 --> Angebot_noch_offen_6496
    Angebot_noch_offen_Ja_6272(["Angebot_noch_offen – Ja"])
    Angebot_noch_offen_6496 -->|Ja| Angebot_noch_offen_Ja_6272
    E_Mail_senden_V2_7168["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_Ja_6272 --> E_Mail_senden_V2_7168
    E_Mail_senden_V2_6720["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_6496 --> E_Mail_senden_V2_6720
    Setze_VDatumAngebotErstellt_496["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_48 --> Setze_VDatumAngebotErstellt_496
    Variable_festlegen_9824["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_496 --> Variable_festlegen_9824
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__272{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_9824 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__272
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__720(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__272 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__720
    E_Mail_senden_V2_2_1392["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__720 --> E_Mail_senden_V2_2_1392
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1168(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__272 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1168
    Auftrag_gewonnen_1840{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1168 --> Auftrag_gewonnen_1840
    Auftrag_gewonnen_Ja_2288(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_1840 -->|Ja| Auftrag_gewonnen_Ja_2288
    Auftragsnummer_bekannt_2960{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_2288 --> Auftragsnummer_bekannt_2960
    Auftragsnummer_bekannt_Nein_2736(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_2960 -->|Nein| Auftragsnummer_bekannt_Nein_2736
    E_Mail_senden_V2_3_3408["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_2736 --> E_Mail_senden_V2_3_3408
    Auftragsnummer_bekannt_2064{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_1840 --> Auftragsnummer_bekannt_2064
    Auftragsnummer_bekannt_Nein_1616(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_2064 -->|Nein| Auftragsnummer_bekannt_Nein_1616
    E_Mail_senden_V2_3_2512["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_1616 --> E_Mail_senden_V2_3_2512
    E_Mail_senden_V2_2_944["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__272 --> E_Mail_senden_V2_2_944
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6416{{"Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt"}}
    Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__9040 --> Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6416
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4672(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Ja"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6416 -->|Ja| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4672
    Setze_VDatumAngebotErstellt_5568["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4672 --> Setze_VDatumAngebotErstellt_5568
    Variable_festlegen_5120["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_5568 --> Variable_festlegen_5120
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5344{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_5120 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5344
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5792(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5344 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5792
    E_Mail_senden_V2_2_6464["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5792 --> E_Mail_senden_V2_2_6464
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6240(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5344 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6240
    Auftrag_gewonnen_6912{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6240 --> Auftrag_gewonnen_6912
    Auftrag_gewonnen_Ja_7360(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_6912 -->|Ja| Auftrag_gewonnen_Ja_7360
    Auftragsnummer_bekannt_8032{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_7360 --> Auftragsnummer_bekannt_8032
    Auftragsnummer_bekannt_Nein_7808(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_8032 -->|Nein| Auftragsnummer_bekannt_Nein_7808
    E_Mail_senden_V2_3_8480["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_7808 --> E_Mail_senden_V2_3_8480
    Auftragsnummer_bekannt_7136{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_6912 --> Auftragsnummer_bekannt_7136
    Auftragsnummer_bekannt_Nein_6688(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_7136 -->|Nein| Auftragsnummer_bekannt_Nein_6688
    E_Mail_senden_V2_3_7584["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_6688 --> E_Mail_senden_V2_3_7584
    E_Mail_senden_V2_2_6016["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5344 --> E_Mail_senden_V2_2_6016
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_8256(["Status_seit_14_Tagen_abgeschlossen_und_Angebot_erstellt – Nein"])
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6416 -->|Nein| Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_8256
    Angebot_noch_offen_8928{{"Angebot_noch_offen"}}
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_8256 --> Angebot_noch_offen_8928
    Angebot_noch_offen_Ja_8704(["Angebot_noch_offen – Ja"])
    Angebot_noch_offen_8928 -->|Ja| Angebot_noch_offen_Ja_8704
    E_Mail_senden_V2_9600["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_Ja_8704 --> E_Mail_senden_V2_9600
    E_Mail_senden_V2_9152["E-Mail_senden_(V2)\n[Office 365 Outlook]"]
    Angebot_noch_offen_8928 --> E_Mail_senden_V2_9152
    Setze_VDatumAngebotErstellt_6672["Setze_VDatumAngebotErstellt"]
    Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6416 --> Setze_VDatumAngebotErstellt_6672
    Variable_festlegen_2256["Variable_festlegen"]
    Setze_VDatumAngebotErstellt_6672 --> Variable_festlegen_2256
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2496{{"Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen"}}
    Variable_festlegen_2256 --> Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2496
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2656(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Ja"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2496 -->|Ja| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2656
    E_Mail_senden_V2_2_2880["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2656 --> E_Mail_senden_V2_2_2880
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2432(["Angebot_ist_seit__mindestens_14_Tagen_erstellt_und_Auftrag_gewonnen – Nein"])
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2496 -->|Nein| Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2432
    Auftrag_gewonnen_3328{{"Auftrag_gewonnen"}}
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2432 --> Auftrag_gewonnen_3328
    Auftrag_gewonnen_Ja_3776(["Auftrag_gewonnen – Ja"])
    Auftrag_gewonnen_3328 -->|Ja| Auftrag_gewonnen_Ja_3776
    Auftragsnummer_bekannt_4448{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_Ja_3776 --> Auftragsnummer_bekannt_4448
    Auftragsnummer_bekannt_Nein_4224(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_4448 -->|Nein| Auftragsnummer_bekannt_Nein_4224
    E_Mail_senden_V2_3_4896["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_4224 --> E_Mail_senden_V2_3_4896
    Auftragsnummer_bekannt_3552{{"Auftragsnummer_bekannt"}}
    Auftrag_gewonnen_3328 --> Auftragsnummer_bekannt_3552
    Auftragsnummer_bekannt_Nein_3104(["Auftragsnummer_bekannt – Nein"])
    Auftragsnummer_bekannt_3552 -->|Nein| Auftragsnummer_bekannt_Nein_3104
    E_Mail_senden_V2_3_4000["E-Mail_senden_(V2)_3\n[Office 365 Outlook]"]
    Auftragsnummer_bekannt_Nein_3104 --> E_Mail_senden_V2_3_4000
    E_Mail_senden_V2_2_2208["E-Mail_senden_(V2)_2\n[Office 365 Outlook]"]
    Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2496 --> E_Mail_senden_V2_2_2208
    FLOW_END(["Ende"])
    E_Mail_senden_V2_2_5200 --> FLOW_END
    E_Mail_senden_V2_3_6048 --> FLOW_END
    E_Mail_senden_V2_3_5152 --> FLOW_END
    E_Mail_senden_V2_2_4752 --> FLOW_END
    E_Mail_senden_V2_7168 --> FLOW_END
    E_Mail_senden_V2_6720 --> FLOW_END
    E_Mail_senden_V2_2_1392 --> FLOW_END
    E_Mail_senden_V2_3_3408 --> FLOW_END
    E_Mail_senden_V2_3_2512 --> FLOW_END
    E_Mail_senden_V2_2_944 --> FLOW_END
    E_Mail_senden_V2_2_6464 --> FLOW_END
    E_Mail_senden_V2_3_8480 --> FLOW_END
    E_Mail_senden_V2_3_7584 --> FLOW_END
    E_Mail_senden_V2_2_6016 --> FLOW_END
    E_Mail_senden_V2_9600 --> FLOW_END
    E_Mail_senden_V2_9152 --> FLOW_END
    E_Mail_senden_V2_2_2880 --> FLOW_END
    E_Mail_senden_V2_3_4896 --> FLOW_END
    E_Mail_senden_V2_3_4000 --> FLOW_END
    E_Mail_senden_V2_2_2208 --> FLOW_END

    class TRIGGER trigger
    class VZeitStempelStatusAbgeschlossen_3632 variable
    class VZeitStempelAngebotErstellt_3008 variable
    class VEndDatum_4608 variable
    class VTempCheckIfNull_9520 variable
    class Elemente_abrufen_alle_Presales_Projekte_128 connector
    class Check_Status_Abgeschlossen_5424 loop
    class Setze_VDatumStatusAbgeschlossen_7680 variable
    class Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__9040 condition
    class Bedingung_E_Mail_Flow_Aktiv_und_ZeitStempel_nicht__9376 branch_true
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_48 condition
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_3184 branch_true
    class Setze_VDatumAngebotErstellt_4080 variable
    class Variable_festlegen_3632 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4304 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4528 branch_true
    class E_Mail_senden_V2_2_5200 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__4976 branch_false
    class Auftrag_gewonnen_5648 condition
    class Auftrag_gewonnen_Ja_4928 branch_true
    class Auftragsnummer_bekannt_5600 condition
    class Auftragsnummer_bekannt_Nein_5376 branch_false
    class E_Mail_senden_V2_3_6048 connector
    class Auftragsnummer_bekannt_5872 condition
    class Auftragsnummer_bekannt_Nein_5424 branch_false
    class E_Mail_senden_V2_3_5152 connector
    class E_Mail_senden_V2_2_4752 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_5824 branch_false
    class Angebot_noch_offen_6496 condition
    class Angebot_noch_offen_Ja_6272 branch_true
    class E_Mail_senden_V2_7168 connector
    class E_Mail_senden_V2_6720 connector
    class Setze_VDatumAngebotErstellt_496 variable
    class Variable_festlegen_9824 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__272 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__720 branch_true
    class E_Mail_senden_V2_2_1392 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__1168 branch_false
    class Auftrag_gewonnen_1840 condition
    class Auftrag_gewonnen_Ja_2288 branch_true
    class Auftragsnummer_bekannt_2960 condition
    class Auftragsnummer_bekannt_Nein_2736 branch_false
    class E_Mail_senden_V2_3_3408 connector
    class Auftragsnummer_bekannt_2064 condition
    class Auftragsnummer_bekannt_Nein_1616 branch_false
    class E_Mail_senden_V2_3_2512 connector
    class E_Mail_senden_V2_2_944 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_6416 condition
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_4672 branch_true
    class Setze_VDatumAngebotErstellt_5568 variable
    class Variable_festlegen_5120 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5344 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__5792 branch_true
    class E_Mail_senden_V2_2_6464 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__6240 branch_false
    class Auftrag_gewonnen_6912 condition
    class Auftrag_gewonnen_Ja_7360 branch_true
    class Auftragsnummer_bekannt_8032 condition
    class Auftragsnummer_bekannt_Nein_7808 branch_false
    class E_Mail_senden_V2_3_8480 connector
    class Auftragsnummer_bekannt_7136 condition
    class Auftragsnummer_bekannt_Nein_6688 branch_false
    class E_Mail_senden_V2_3_7584 connector
    class E_Mail_senden_V2_2_6016 connector
    class Status_seit_14_Tagen_abgeschlossen_und_Angebot_ers_8256 branch_false
    class Angebot_noch_offen_8928 condition
    class Angebot_noch_offen_Ja_8704 branch_true
    class E_Mail_senden_V2_9600 connector
    class E_Mail_senden_V2_9152 connector
    class Setze_VDatumAngebotErstellt_6672 variable
    class Variable_festlegen_2256 variable
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2496 condition
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2656 branch_true
    class E_Mail_senden_V2_2_2880 connector
    class Angebot_ist_seit_mindestens_14_Tagen_erstellt_und__2432 branch_false
    class Auftrag_gewonnen_3328 condition
    class Auftrag_gewonnen_Ja_3776 branch_true
    class Auftragsnummer_bekannt_4448 condition
    class Auftragsnummer_bekannt_Nein_4224 branch_false
    class E_Mail_senden_V2_3_4896 connector
    class Auftragsnummer_bekannt_3552 condition
    class Auftragsnummer_bekannt_Nein_3104 branch_false
    class E_Mail_senden_V2_3_4000 connector
    class E_Mail_senden_V2_2_2208 connector
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

