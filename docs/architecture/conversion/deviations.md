# Deviations from Apache Atlas

Every behaviour of Aurelius Atlas that a client could observe and that differs from Apache Atlas
2.4.0 ([ADR 046](../adr/046-the-catalogue-keeps-its-public-contract.md)). The parity report links
each tolerated difference to its entry here; a difference without an entry is a defect.

| #     | Area          | Apache Atlas behaviour                                    | Aurelius Atlas behaviour | Reason                                                                                   | Increment |
| ----- | ------------- | --------------------------------------------------------- | ------------------------ | ---------------------------------------------------------------------------------------- | --------- |
| DV-01 | Notifications | Publishes entity changes to Kafka; consumes hook messages | Not supported            | Out of scope ([ADR 050](../adr/050-the-system-carries-only-what-the-catalogue-needs.md)) | 0.1       |
| DV-02 | Authorization | Ranger or simple authorizer                               | Simple authorizer only   | Out of scope; Ranger needs its own server                                                | 0.1       |
