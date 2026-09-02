from applypilot.adapters.jobs.ashby import AshbyAdapter
from applypilot.adapters.jobs.greenhouse import GreenhouseAdapter
from applypilot.adapters.jobs.lever import LeverAdapter
from applypilot.adapters.jobs.remotive import RemotiveAdapter

ADAPTERS = {
    item.provider: item
    for item in (GreenhouseAdapter(), LeverAdapter(), AshbyAdapter(), RemotiveAdapter())
}
