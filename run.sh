#!/bin/bash

export PV_SECRET="supersecret"

uvicorn privatevault.context.api.server:app   --host 0.0.0.0   --port 8001   --reload
