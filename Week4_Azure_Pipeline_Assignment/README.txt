# Azure Cloud Fundamentals and Data Pipeline Implementation using ADF

## Objective
To understand Azure cloud concepts and build an end-to-end data pipeline using Azure Storage Account and Azure Data Factory.

## Services Used
- Azure Resource Group
- Azure Storage Account
- Azure Blob Storage
- Azure Data Factory
- Azure IAM

## Pipeline Flow

CSV File (Source Container)
        │
        ▼
Get Metadata Activity
        │
        ▼
Copy Data Activity
        │
        ▼
Destination Container

## Activities Performed

- Created Resource Group
- Created Storage Account
- Created Blob Containers
- Uploaded CSV File
- Created Azure Data Factory
- Created Linked Service
- Created Source and Destination Datasets
- Configured Get Metadata Activity
- Configured Copy Data Activity
- Executed Pipeline Successfully
- Verified Output File
- Assigned IAM Roles

## Result

The pipeline executed successfully. The CSV file was copied from the source container to the destination container, and file metadata was successfully retrieved using the Get Metadata activity.