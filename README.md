# sandbox_ATIA-data-pipelines
experimenting with a multisource data model to estimate GC compliance with Proactive Publication requirements

```mermaid
graph TD
    A[Schedule/Manual Trigger] --> B[Refresh minister.json]
    B --> C[Update ministers with witness ID]
    B --> D[Create transition binder deadline CSV]
    C --> E[Filter witness meetings]

    subgraph Extract - refresh_ministers_json.py
        I1["Fetch XML Data EN - 
         https://www.ourcommons.ca/Members/en/ministries/xml"]
        I2["Fetch XML Data FR -
         https://www.ourcommons.ca/Members/fr/ministries/xml"]
        I3["Load Existing minister.json 
        from ckanext-canada or current repo"]
    end

    subgraph Transform
        T1[Parse XML Data]
        T2[Update JSON with witness IDs]
        T3[Calculate deadlines]
        T4[Filter Meetings]
    end

    subgraph Load
        L1[Save Updated minister.json]
        L2[Save output.csv]
        L3[Save minister_transition_binder_deadline.csv]
        L4[Save minister_parl_comm_deadlines.csv]
    end

    I1 --> B
    I2 --> B
    I3 --> B
    B --> T1
    T1 --> T2
    T2 --> L1
    C --> T3
    T3 --> L2
    D --> T4
    T4 --> L3
    E --> L4

    B --> |Needs: refresh_minister_json| C
    B --> |Needs: refresh_minister_json| D
    C --> |Needs: update_ministers_with_witness_id| E

```
| File | Flat Viewer |
|--|--|
|**minister_transition_binder_deadline.csv**  deadlines for ministerial transition materials to be published, based on 120 days after appointment.  | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/PatLittle/sandbox_ATIA-data-pipelines?filename=minister_transition_binder_deadline.csv)|
|**minister_parl_comm_deadlines.csv**  deadlines for Parliamentry Committee materials to be published, based on 120 days after appointment.  | [![Static Badge](https://img.shields.io/badge/Open%20in%20Flatdata%20Viewer-FF00E8?style=for-the-badge&logo=github&logoColor=black)](https://flatgithub.com/PatLittle/sandbox_ATIA-data-pipelines?filename=minister_parl_comm_deadlines.csv)|