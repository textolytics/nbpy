# Architecture of Jupyter notebook 

The tables below show the current RESTful web service architecture implemented in Jupyter notebook. The listed URL's use the HTTP verbs to return representations of the desired resource.

We are in the process of creating a new dashboard architecture for the Jupyter notebook, which will allow the user to navigate through multiple directory files to find desired notebooks.

The schema is [here](https://github.com/jupyter/notebook/blob/master/notebook/services/api/api.yaml), rendered nicely [here](http://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyter/notebook/master/notebook/services/api/api.yaml).

## Current Architecture ##

Miscellaneous

| HTTP verb | URL | Action |
|:---:|:---:|:---|
| ```GET``` | /.*/ | Strips trailing slashes. |
| ```GET``` | /api | Returns api version information. |
| ```*``` | /api/notebooks | Deprecated: redirect to /api/contents |
| ```GET``` | /api/nbconvert | |

## Notebook and file contents API

| HTTP verb | URL | Action |
|:---:|:---:|:---|
| ```GET``` | /api/contents | Return a model for the base directory. See /api/contents/\<path\>/\<file\>. |
| ```GET``` | /api/contents<br>/\<file\> | Return a model for the given file in the base directory. See /api/contents/\<path\>/\<file\>.|
| ```GET``` | /api/contents<br>/\<path\>/\<file\> | Return a model for a file or directory.  A directory model contains a list of models (without content) of the files and directories it contains. |
| ```PUT``` | /api/contents<br>/\<path\>/\<file\> | Saves the file in the location specified by name and path. PUT is very similar to POST, but the requester specifies the name, whereas with POST, the server picks the name. PUT /api/contents/path/Name.ipynb Save notebook at ``path/Name.ipynb``. Notebook structure is specified in `content` key of JSON request body. If content is not specified, create a new empty notebook. PUT /api/contents/path/Name.ipynb with JSON body::{ "copy_from" : "[path/to/]OtherNotebook.ipynb" } Copy OtherNotebook to Name | 
| ```PATCH``` | /api/contents<br>/\<path\>/\<file\> | PATCH renames a notebook without re-uploading content. |
| ```POST``` | /api/contents<br>/\<path\>/\<file\> | Create a new file or directory in the specified path. POST creates new files or directories. The server always decides on the name. POST /api/contents/path New untitled notebook in path. If content specified, upload a notebook, otherwise start empty. POST /api/contents/path with body {"copy_from" : "OtherNotebook.ipynb"} New copy of OtherNotebook in path |
| ```DELETE``` | /api/contents<br>/\<path\>/\<file\> | delete a file in the given path | 
| ```GET``` | /api/contents<br>/\<path\>/\<file\><br>/checkpoints | get lists checkpoints for a file. |
| ```POST``` | /api/contents<br>/\<path\>/\<file\><br>/checkpoints | post creates a new checkpoint. |
| ```POST``` | /api/contents<br>/\<path\>/\<file\><br>/checkpoints/\<checkpoint_id\> | post restores a file from a checkpoint. |
| ```DELETE``` | /api/contents<br>/\<path\>/\<file\><br>/checkpoints/\<checkpoint_id\> | delete clears a checkpoint for a given file. |

## Kernel API

| HTTP verb | URI | Action |
|:---:|:---:|:---|
| ```GET``` | /api/kernels | Return a model of all kernels. |
| ```GET``` | /api/kernels<br>/\<kernel_id\> | Return a model of kernel with given kernel id. |
| ```POST``` | /api/kernels | Start a new kernel with default or given name. |
| ```DELETE``` | /api/kernels<br>/\<kernel_id\> | Shutdown the given kernel. |
| ```POST``` | /api/kernels<br>/\<kernel_id\>/\<action\> | Perform action on kernel with given kernel id. Actions can be "interrupt" or "restart". |
| ```WS``` | /api/kernels<br>/\<kernel_id\>/channels | Websocket stream |

## Kernelspecs API

| HTTP verb | URI | Action |
|:---:|:---:|:---|
| ```GET``` | /api/kernelspecs | Return a spec model of all available kernels. |
| ```GET``` | /api/kernelspecs<br>/\<kernel_name\> | Return a spec model of available kernels with given kernel name. |

## Sessions API

| HTTP verb | URL | Action |
|:---:|:---:|:---|
| ```GET``` | /api/sessions | Return model of active sessions. |
| ```POST``` | /api/sessions | If session does not already exist, create a new session with given notebook name and path and given kernel name. Return active session. |
| ```GET``` | /api/sessions<br>/\<session_id\> | Return model of active session with given session id. |
| ```PATCH``` | /api/sessions<br>/\<session_id\> | Change notebook name or path of session with given session id. |
| ```DELETE``` | /api/sessions<br>/\<session_id\> | Delete active session with given session id. |

## Clusters API

| HTTP verb | URL | Action |
|:---:|:---:|:---|
| ```GET``` | /api/clusters | Return model of clusters. |
| ```GET``` | /api/clusters<br>/\<cluster_id\> | Return model of given cluster. |
| ```POST``` | /api/clusters<br>/\<cluster_id\>/\<action\> | Perform action with given clusters. Valid actions are "start" or "stop" |

### Old Architecture

This chart shows the web-services in the single directory Jupyter notebook. 

| HTTP verb | URL | Action |
|:---:|:---:|:---|
| ```GET``` | /notebooks | returns list of dicts with each notebook's info |
| ```POST``` | /notebooks | if sending a body, saving that body as a new notebook; if no body, create a new notebooks | 
| ```GET``` | /notebooks/\<notebook_id\> | get JSON data for notebook |
| ```PUT``` | /notebooks/\<notebook_id\> | saves an existing notebook with body data |
| ```DELETE``` | /notebooks/\<notebook_id\> | deletes the notebook with the given ID | 

This chart shows the architecture for the Jupyter notebook.

| HTTP verb | URI | Action |
|:---:|:---:|:---|
| ```GET``` | / | navigates user to dashboard of notebooks and clusters |
| ```GET``` | /\<notebook_id\> | go to webpage for that notebook |
| ```GET``` | /new | creates a new notebook with profile (or default, if no profile exists) settings |
| ```GET``` | /\<notebook_id\>/copy | opens a duplicate copy of the notebook with the given ID in a new tab |
| ```GET``` | /\<notebook_id\>/print | prints the notebook with the given ID; if notebook ID doesn't exist, displays error message |
| ```GET``` | /login | navigates to login page; if no user profile is defined, it navigates user to dashboard|
| ```GET``` | /logout | logs out of current profile, and navigates user to login page |


This chart shows the Web services that act on the kernels and clusters.

| HTTP verb | URL | Action |
|:---:|:---:|:---|
| ```GET``` | /kernels | return the list of kernel ID's currently running |
| ```GET``` | /kernels/\<kernel_id\> | --- |
| ```GET``` | /kernels/\<kernel_id\>/\<kernel_action\>| performs action (restart/kill) kernel with given ID |
| ```GET``` | /kernels/\<kernel_id\>/iopub | --- |
| ```GET``` | /kernels/\<kernel_id\>/shell | --- |
| ```GET``` | /rstservice/render | --- |
| ```GET``` | /files/(.*) | --- |
| ```GET``` | /clusters | returns a list of dicts with each cluster's information |
| ```POST``` | /clusters/\<profile_id\>/\<cluster_action\> | performs action (start/stop) on cluster with given profile ID |
| ```GET``` | /clusters/\<profile_id\> | returns the JSON data for cluster with given profile ID | 
