This is a self documenting REST API Build in Django. The philosophy behind this app is to provide a unified interface that brings together data sources like Active Directory, SCCM, Microsoft Defender, and Cisco Network into a single pane of glass. This foundation enables automation and, more importantly, facilitates informed decision-making through AI-generated lists based on data from these sources.

This app is designed for environments with multiple sub-IT departments, where security restrictions prevent full access to systems like SCCM or Microsoft Defender. For example, a sub-IT department can query SCCM to retrieve a list of all computers in their department, along with the software installed on those computers. This app makes such functionality possible. The web portal offers services through a UI/UX experience built on this app's API. For instance, there is currently a service that allows for MFA resets.



# Features
- [x] Active Directory
- SCCM - still in development
- Microsoft Defender - still in development
- Cisco Network - still in development

# Services
- [x] MFA Reset