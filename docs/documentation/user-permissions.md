# User Permissions

Within the Chatbot application, users can have one of four user roles applied, which sets the allowed permissions within the application. The goal of the user roles is to enable administrators to restrict access to functionality like segregating workspaces based on access groups.

## Access Detail by Role

* **chatbot_user**: 
    * ✅ Access to the Chatbot functionality - both "Playground" (single-model chat) and "Multi-chat Playground" (multi-model chat).
    * ✅ View the list of models
    * ⛔️ Use existing RAG workspaces within a chat
    * ⛔️ Browse RAG Workspaces
    * ⛔️ Access RAG Workpsace Details
    * ⛔️ Add Content to a RAG Workspace
    * ⛔️ Create, Update or Delete RAG Workspaces
    * ⛔️ Access Embeddings Demo
    * ⛔️ Access Cross-encoders Demo
    * ⛔️ Access list of available RAG Engines
    * ⛔️ Add, Delete Users from workspaces
    * ⛔️ Create, Update, Delete Users in the Chatbot Application

* **workspace-read-<workspace_id>**
    * ✅ Access to the Chatbot functionality - both "Playground" (single-model chat) and "Multi-chat Playground" (multi-model chat).
    * ✅ Use existing RAG workspaces within a chat where they are a member
    * ✅ View the list of models
    * ✅ Browse RAG Workspaces where they are a member
    * ✅ Access RAG Workpsace Details where they are a member
    * ⛔️ Add/Remove Content to a RAG workspace
    * ⛔️ Create, Update or Delete RAG workspaces
    * ✅ Access embeddings demo
    * ✅ Access cross-encoders demo
    * ✅ Access list of available RAG engines
    * ⛔️ Add, Delete Users from workspaces
    * ⛔️ Create, Update, Delete Users in the Chatbot Application

* **workspace-write-<workspace_id>**
    * ✅ Access to the Chatbot functionality - both "Playground" (single-model chat) and "Multi-chat Playground" (multi-model chat).
    * ✅ Use existing RAG workspaces within a chat where they are a member
    * ✅ View the list of models
    * ✅ Browse RAG workspaces Where they are a member
    * ✅ Access a RAG workspace Details where they are a member
    * ✅️ Add/Remove Content to a RAG workspace
    * ⛔️ Create, Update or Delete RAG workspaces
    * ✅ Access embeddings demo
    * ✅ Access cross-encoders demo
    * ✅ Access list of available RAG engines
    * ⛔️ Add, Delete Users from workspaces
    * ⛔️ Create, Update, Delete Users in the Chatbot Application

* **chatbot_admin**
    * ✅ Access to the Chatbot functionality - both "Playground" (single-model chat) and "Multi-chat Playground" (multi-model chat).
    * ✅ Use any existing RAG workspaces within a chat
    * ✅ View the list of models
    * ✅ Browse any RAG workspaces
    * ✅ Access any RAG workspace details
    * ✅ Add content to any RAG workspace
    * ✅ Create, Update or Delete RAG workspaces
    * ✅ Access embeddings demo
    * ✅ Access cross-encoders Demo
    * ✅ Access list of available RAG engines
    * ✅️ Add, Delete Users from any workspaces
    * ✅ Create, Update, Delete Users in the Chatbot Application