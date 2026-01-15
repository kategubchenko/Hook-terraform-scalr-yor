# Scalr integration with Bridgecrew Yor via custom hooks

This example shows how to integrate Scalr and Bridgecrew/yor using Custom hooks. 
It helps users to tag all supported resources with dynamic tags. 

The pre-plan hook requires 3 shell variables to be set:

* SCALR_HOSTNAME
* SCALR_TOKEN
* SCALR_RUN_ID

If the run is executed in the Scalr remote backend all those variables are auto-populated in the pipeline.

Pre-plan script will auto-populate tags:

* current run meta-data: id, triggered source, creation date
* workspace meta-data: id, name, environment id, tags
* vcs meta-data if a run is associated with a VCS revision: commit SHA and message, branch, repository, etc.

NOTE: if the hook is executed locally users have you download respective yor release. 
nvb
